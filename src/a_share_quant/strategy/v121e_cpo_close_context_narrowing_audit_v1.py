from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_close(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "close_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) < -0.05
        and _to_float(row.get("max_adverse_return_3d")) < -0.08
    )


def _candidate_score(row: dict[str, Any]) -> float:
    return (
        -_to_float(row.get("f30_afternoon_volume_share_rz"))
        - _to_float(row.get("f60_afternoon_volume_share_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        - _to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("f60_high_time_ratio_rz"))
        - 0.5 * _to_float(row.get("f30_breakout_efficiency_rz"))
        - 0.5 * _to_float(row.get("f60_breakout_efficiency_rz"))
        - 0.25 * _to_float(row.get("f30_close_vs_vwap_rz"))
        - 0.25 * _to_float(row.get("f60_close_vs_vwap_rz"))
    )


@dataclass(slots=True)
class V121ECpoCloseContextNarrowingAuditReport:
    summary: dict[str, Any]
    threshold_audit_rows: list[dict[str, Any]]
    scored_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_audit_rows": self.threshold_audit_rows,
            "scored_rows": self.scored_rows,
            "interpretation": self.interpretation,
        }


class V121ECpoCloseContextNarrowingAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V121ECpoCloseContextNarrowingAuditReport:
        rows = [dict(row) for row in _load_csv_rows(rows_path) if str(row.get("action_context")) == "close_vs_hold"]
        scored_rows: list[dict[str, Any]] = []
        for row in rows:
            scored_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "board_phase": str(row["board_phase"]),
                    "positive_close_label": _is_positive_close(row),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "participation_collapse_close_risk_score": round(_candidate_score(row), 6),
                }
            )
        positives = [row for row in scored_rows if row["positive_close_label"]]
        negatives = [row for row in scored_rows if not row["positive_close_label"]]
        thresholds = sorted({_to_float(row["participation_collapse_close_risk_score"]) for row in scored_rows}, reverse=True)

        threshold_audit_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positives if _to_float(row["participation_collapse_close_risk_score"]) >= threshold)
            fp = sum(1 for row in negatives if _to_float(row["participation_collapse_close_risk_score"]) >= threshold)
            tn = len(negatives) - fp
            tpr = tp / len(positives) if positives else 0.0
            tnr = tn / len(negatives) if negatives else 0.0
            record = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "positive_recall": round(tpr, 6),
                "negative_reject_rate": round(tnr, 6),
                "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
            }
            threshold_audit_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        summary = {
            "acceptance_posture": "freeze_v121e_cpo_close_context_narrowing_audit_v1",
            "candidate_discriminator_name": "participation_collapse_close_risk_score_candidate",
            "close_context_row_count": len(scored_rows),
            "positive_close_row_count": len(positives),
            "negative_close_row_count": len(negatives),
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "positive_recall_at_best_threshold": best_row["positive_recall"] if best_row else 0.0,
            "negative_reject_rate_at_best_threshold": best_row["negative_reject_rate"] if best_row else 0.0,
            "recommended_next_posture": "chronology_audit_inside_close_context_only",
        }
        interpretation = [
            "V1.21E narrows the first downside branch to the only context where it shows actual discrimination: close_vs_hold.",
            "This does not promote the branch; it only tests whether the broad risk prior becomes useful once the action context is held fixed.",
            "If the line stays weak even here, it should remain soft-only and stop consuming candidate budget.",
        ]
        return V121ECpoCloseContextNarrowingAuditReport(
            summary=summary,
            threshold_audit_rows=threshold_audit_rows,
            scored_rows=scored_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121ECpoCloseContextNarrowingAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121ECpoCloseContextNarrowingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121e_cpo_close_context_narrowing_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

