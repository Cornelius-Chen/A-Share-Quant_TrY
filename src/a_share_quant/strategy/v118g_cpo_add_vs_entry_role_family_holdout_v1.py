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


def _is_entry(row: dict[str, Any]) -> bool:
    return str(row.get("action_context")) == "entry_vs_skip"


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
class V118GCpoAddVsEntryRoleFamilyHoldoutReport:
    summary: dict[str, Any]
    holdout_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "holdout_rows": self.holdout_rows,
            "interpretation": self.interpretation,
        }


class V118GCpoAddVsEntryRoleFamilyHoldoutAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118GCpoAddVsEntryRoleFamilyHoldoutReport:
        rows = [row for row in _load_csv_rows(rows_path) if _is_positive_add(row) or _is_entry(row)]
        role_families = sorted({str(row.get("role_family")) for row in rows})
        holdout_rows: list[dict[str, Any]] = []

        for holdout_role in role_families:
            train_rows = [row for row in rows if str(row.get("role_family")) != holdout_role]
            test_rows = [row for row in rows if str(row.get("role_family")) == holdout_role]
            thresholds = sorted({_candidate_score(row) for row in train_rows}, reverse=True)

            best_threshold = 0.0
            best_train_bal = -1.0
            for threshold in thresholds:
                train_pos = [row for row in train_rows if _is_positive_add(row)]
                train_neg = [row for row in train_rows if _is_entry(row)]
                tpr = sum(1 for row in train_pos if _candidate_score(row) >= threshold) / len(train_pos) if train_pos else 0.0
                tnr = sum(1 for row in train_neg if _candidate_score(row) < threshold) / len(train_neg) if train_neg else 0.0
                bal = (tpr + tnr) / 2.0
                if bal > best_train_bal:
                    best_train_bal = bal
                    best_threshold = threshold

            test_pos = [row for row in test_rows if _is_positive_add(row)]
            test_neg = [row for row in test_rows if _is_entry(row)]
            test_tpr = sum(1 for row in test_pos if _candidate_score(row) >= best_threshold) / len(test_pos) if test_pos else None
            test_tnr = sum(1 for row in test_neg if _candidate_score(row) < best_threshold) / len(test_neg) if test_neg else None
            test_bal = None
            if test_tpr is not None and test_tnr is not None:
                test_bal = (test_tpr + test_tnr) / 2.0

            holdout_rows.append(
                {
                    "holdout_role_family": holdout_role,
                    "train_best_threshold": round(best_threshold, 6),
                    "train_best_balanced_accuracy": round(best_train_bal, 6),
                    "test_positive_add_recall": None if test_tpr is None else round(test_tpr, 6),
                    "test_entry_reject_rate": None if test_tnr is None else round(test_tnr, 6),
                    "test_balanced_accuracy": None if test_bal is None else round(test_bal, 6),
                    "test_positive_add_count": len(test_pos),
                    "test_entry_count": len(test_neg),
                }
            )

        evaluable = [row["test_balanced_accuracy"] for row in holdout_rows if row["test_balanced_accuracy"] is not None]
        summary = {
            "acceptance_posture": "freeze_v118g_cpo_add_vs_entry_role_family_holdout_v1",
            "holdout_count": len(holdout_rows),
            "evaluable_holdout_count": len(evaluable),
            "mean_evaluable_test_balanced_accuracy": round(sum(evaluable) / len(evaluable), 6) if evaluable else 0.0,
            "min_evaluable_test_balanced_accuracy": round(min(evaluable), 6) if evaluable else 0.0,
            "recommended_next_posture": "audit_whether_chronology_instability_is_really_role_year_entanglement",
        }
        interpretation = [
            "V1.18G tests whether the add-vs-entry branch is really learning an action distinction or merely overfitting specific role families and years.",
            "If role holdouts break the branch badly, chronology instability may actually be an object-shift problem in disguise.",
            "This remains a non-replay candidate audit only.",
        ]
        return V118GCpoAddVsEntryRoleFamilyHoldoutReport(
            summary=summary,
            holdout_rows=holdout_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118GCpoAddVsEntryRoleFamilyHoldoutReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118GCpoAddVsEntryRoleFamilyHoldoutAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118g_cpo_add_vs_entry_role_family_holdout_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
