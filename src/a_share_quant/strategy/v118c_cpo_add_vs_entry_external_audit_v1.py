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
class V118CCpoAddVsEntryExternalAuditReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V118CCpoAddVsEntryExternalAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118CCpoAddVsEntryExternalAuditReport:
        rows = _load_csv_rows(rows_path)
        positives = [row for row in rows if _is_positive_add(row)]
        negatives = [row for row in rows if str(row.get("action_context")) == "entry_vs_skip"]
        thresholds = sorted({_candidate_score(row) for row in positives + negatives}, reverse=True)

        threshold_rows: list[dict[str, Any]] = []
        best_row: dict[str, Any] | None = None
        for threshold in thresholds:
            tp = sum(1 for row in positives if _candidate_score(row) >= threshold)
            fn = len(positives) - tp
            fp = sum(1 for row in negatives if _candidate_score(row) >= threshold)
            tn = len(negatives) - fp
            pos_recall = tp / len(positives) if positives else 0.0
            entry_reject = tn / len(negatives) if negatives else 0.0
            record = {
                "threshold": round(threshold, 6),
                "tp": tp,
                "fn": fn,
                "fp": fp,
                "tn": tn,
                "positive_add_recall": round(pos_recall, 6),
                "entry_reject_rate": round(entry_reject, 6),
                "balanced_accuracy": round((pos_recall + entry_reject) / 2.0, 6),
            }
            threshold_rows.append(record)
            if best_row is None or record["balanced_accuracy"] > best_row["balanced_accuracy"]:
                best_row = record

        pos_mean = sum(_candidate_score(row) for row in positives) / len(positives)
        neg_mean = sum(_candidate_score(row) for row in negatives) / len(negatives)
        summary = {
            "acceptance_posture": "freeze_v118c_cpo_add_vs_entry_external_audit_v1",
            "candidate_name": "add_vs_strong_entry_separation_score_candidate",
            "positive_add_mean_score": round(pos_mean, 6),
            "entry_mean_score": round(neg_mean, 6),
            "mean_gap_positive_add_minus_entry": round(pos_mean - neg_mean, 6),
            "best_threshold": best_row["threshold"] if best_row else 0.0,
            "best_balanced_accuracy": best_row["balanced_accuracy"] if best_row else 0.0,
            "recommended_next_posture": "time_split_validate_add_vs_entry_discriminator_before_any_further_candidate_commitment",
        }
        interpretation = [
            "V1.18C expands the new discriminator to the full positive-add versus all-entry surface, not just the leaked-entry subset.",
            "This is the first real external audit of whether the branch is solving the correct problem: add-vs-entry discrimination rather than generic false-positive control.",
            "If this does not separate add from entry cleanly enough, the branch should die quickly instead of becoming another same-family tunnel.",
        ]
        return V118CCpoAddVsEntryExternalAuditReport(
            summary=summary,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118CCpoAddVsEntryExternalAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118CCpoAddVsEntryExternalAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118c_cpo_add_vs_entry_external_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
