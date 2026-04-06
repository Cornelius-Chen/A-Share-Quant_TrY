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
class V118DCpoAddVsEntryTimeSplitValidationReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V118DCpoAddVsEntryTimeSplitValidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118DCpoAddVsEntryTimeSplitValidationReport:
        rows = [
            row
            for row in _load_csv_rows(rows_path)
            if _is_positive_add(row) or str(row.get("action_context")) == "entry_vs_skip"
        ]
        split_specs = [
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        ]
        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_specs:
            train_rows = [row for row in rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in rows if str(row["signal_trade_date"])[:4] in holdout_years]
            thresholds = sorted({_candidate_score(row) for row in train_rows}, reverse=True)

            best_threshold = 0.0
            best_train_bal = -1.0
            for threshold in thresholds:
                train_pos = [row for row in train_rows if _is_positive_add(row)]
                train_neg = [row for row in train_rows if not _is_positive_add(row)]
                tp = sum(1 for row in train_pos if _candidate_score(row) >= threshold)
                tn = sum(1 for row in train_neg if _candidate_score(row) < threshold)
                pos_recall = tp / len(train_pos) if train_pos else 0.0
                neg_reject = tn / len(train_neg) if train_neg else 0.0
                bal = (pos_recall + neg_reject) / 2.0
                if bal > best_train_bal:
                    best_train_bal = bal
                    best_threshold = threshold

            test_pos = [row for row in test_rows if _is_positive_add(row)]
            test_neg = [row for row in test_rows if not _is_positive_add(row)]
            test_tp = sum(1 for row in test_pos if _candidate_score(row) >= best_threshold)
            test_tn = sum(1 for row in test_neg if _candidate_score(row) < best_threshold)
            test_pos_recall = test_tp / len(test_pos) if test_pos else 0.0
            test_entry_reject = test_tn / len(test_neg) if test_neg else 0.0
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_best_threshold": round(best_threshold, 6),
                    "train_best_balanced_accuracy": round(best_train_bal, 6),
                    "test_balanced_accuracy": round((test_pos_recall + test_entry_reject) / 2.0, 6),
                    "test_positive_add_recall": round(test_pos_recall, 6),
                    "test_entry_reject_rate": round(test_entry_reject, 6),
                }
            )

        mean_test_bal = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test_bal = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        summary = {
            "acceptance_posture": "freeze_v118d_cpo_add_vs_entry_time_split_validation_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test_bal, 6),
            "min_test_balanced_accuracy": round(min_test_bal, 6),
            "stability_posture": (
                "candidate_unstable_under_time_split"
                if min_test_bal < 0.55
                else "candidate_stable_enough_for_next_triage"
            ),
            "recommended_next_posture": "send_BCD_to_three_run_adversarial_review",
        }
        interpretation = [
            "V1.18D does not ask whether the add-vs-entry discriminator looks neat on the full table. It asks whether the separation survives crude chronology.",
            "If not, the branch should stay candidate-only or die quickly instead of becoming the next mainline distraction.",
            "This closes the first candidate cycle for the add-vs-entry branch.",
        ]
        return V118DCpoAddVsEntryTimeSplitValidationReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118DCpoAddVsEntryTimeSplitValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118DCpoAddVsEntryTimeSplitValidationAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118d_cpo_add_vs_entry_time_split_validation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
