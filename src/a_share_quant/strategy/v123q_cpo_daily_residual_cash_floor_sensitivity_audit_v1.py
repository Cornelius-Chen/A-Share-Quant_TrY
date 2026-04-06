from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v123_daily_residual_downside_utils import (
    build_daily_residual_downside_sample,
    chronological_split_rows,
    score_daily_residual_candidates,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V123QCpoDailyResidualCashFloorSensitivityAuditReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "interpretation": self.interpretation,
        }


class V123QCpoDailyResidualCashFloorSensitivityAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123QCpoDailyResidualCashFloorSensitivityAuditReport:
        threshold_rows: list[dict[str, Any]] = []
        for cash_floor in (0.55, 0.60, 0.65, 0.70):
            dataset = build_daily_residual_downside_sample(repo_root=self.repo_root, cash_ratio_floor=cash_floor)
            scored_rows, candidate_rows = score_daily_residual_candidates(dataset.sample_rows)
            target_row = next(row for row in candidate_rows if row["candidate_name"] == "held_pair_deterioration_score")
            split_rows = chronological_split_rows(rows=scored_rows, score_field="held_pair_deterioration_score")
            mean_test = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
            min_test = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
            threshold_rows.append(
                {
                    "cash_ratio_floor": cash_floor,
                    "sample_row_count": len(scored_rows),
                    "positive_row_count": sum(1 for row in scored_rows if bool(row["positive_label"])),
                    "negative_row_count": sum(1 for row in scored_rows if not bool(row["positive_label"])),
                    "discovery_gap": target_row["discovery_mean_gap_positive_minus_negative"],
                    "q75_balanced_accuracy": target_row["q75_balanced_accuracy"],
                    "time_split_mean_balanced_accuracy": round(mean_test, 6),
                    "time_split_min_balanced_accuracy": round(min_test, 6),
                }
            )

        stable_rows = [
            row
            for row in threshold_rows
            if _to_float(row["q75_balanced_accuracy"]) > 0.55
            and _to_float(row["time_split_min_balanced_accuracy"]) > 0.54
        ]
        summary = {
            "acceptance_posture": "freeze_v123q_cpo_daily_residual_cash_floor_sensitivity_audit_v1",
            "candidate_name": "held_pair_deterioration_score",
            "cash_floor_count": len(threshold_rows),
            "stable_cash_floor_count": len(stable_rows),
            "cash_floor_sensitivity_posture": (
                "stable_across_adjacent_cash_floors" if len(stable_rows) >= 2 else "too_sensitive_to_cash_floor"
            ),
            "recommended_next_posture": "continue_only_if_residual_branch_is_not_overly_cash_floor_specific",
        }
        interpretation = [
            "V1.23Q checks whether the residual downside branch only works because the high-cash subset was carved at exactly 60%.",
            "A branch that survives adjacent cash floors is more credible as a real residual downside signal rather than a threshold artifact.",
            "This remains non-replay and narrow by design.",
        ]
        return V123QCpoDailyResidualCashFloorSensitivityAuditReport(
            summary=summary,
            threshold_rows=threshold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123QCpoDailyResidualCashFloorSensitivityAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123QCpoDailyResidualCashFloorSensitivityAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123q_cpo_daily_residual_cash_floor_sensitivity_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
