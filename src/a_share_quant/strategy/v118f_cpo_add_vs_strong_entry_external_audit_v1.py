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


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _is_strong_entry(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "entry_vs_skip"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and (
            str(row.get("action_favored_3d")) == "True"
            or _to_float(row.get("max_adverse_return_3d")) > -0.04
        )
    )


def _candidate_score(row: dict[str, Any]) -> float:
    return (
        _to_float(row.get("f30_breakout_efficiency_rz"))
        + _to_float(row.get("f60_breakout_efficiency_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f60_last_bar_return_rz"))
    )


@dataclass(slots=True)
class V118FCpoAddVsStrongEntryExternalAuditReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V118FCpoAddVsStrongEntryExternalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118FCpoAddVsStrongEntryExternalAuditReport:
        rows = _load_csv_rows(rows_path)
        positives = [row for row in rows if _is_positive_add(row)]
        negatives = [row for row in rows if _is_strong_entry(row)]
        thresholds = sorted({_candidate_score(row) for row in positives + negatives}, reverse=True)

        threshold_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positives if _candidate_score(row) >= threshold)
            fn = len(positives) - tp
            fp = sum(1 for row in negatives if _candidate_score(row) >= threshold)
            tn = len(negatives) - fp
            pos_recall = tp / len(positives) if positives else 0.0
            strong_entry_reject = tn / len(negatives) if negatives else 0.0
            record = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_add_recall": round(pos_recall, 6),
                "strong_entry_reject_rate": round(strong_entry_reject, 6),
                "balanced_accuracy": round((pos_recall + strong_entry_reject) / 2.0, 6),
            }
            threshold_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        pos_mean = sum(_candidate_score(row) for row in positives) / len(positives)
        neg_mean = sum(_candidate_score(row) for row in negatives) / len(negatives)
        summary = {
            "acceptance_posture": "freeze_v118f_cpo_add_vs_strong_entry_external_audit_v1",
            "candidate_name": "add_vs_strong_entry_separation_score_candidate",
            "positive_add_row_count": len(positives),
            "strong_entry_row_count": len(negatives),
            "positive_add_mean_score": round(pos_mean, 6),
            "strong_entry_mean_score": round(neg_mean, 6),
            "mean_gap_positive_add_minus_strong_entry": round(pos_mean - neg_mean, 6),
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "recommended_next_posture": "challenge_candidate_under_role_family_holdout_before_any_further_branch_commitment",
        }
        interpretation = [
            "V1.18F hardens the problem surface by comparing positive add windows only against strong entry windows, not all entry windows.",
            "If the branch cannot separate add from the strongest entry lookalikes, then the previous V118C result was too easy.",
            "This is still candidate-only and non-replay.",
        ]
        return V118FCpoAddVsStrongEntryExternalAuditReport(
            summary=summary,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118FCpoAddVsStrongEntryExternalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118FCpoAddVsStrongEntryExternalAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118f_cpo_add_vs_strong_entry_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
