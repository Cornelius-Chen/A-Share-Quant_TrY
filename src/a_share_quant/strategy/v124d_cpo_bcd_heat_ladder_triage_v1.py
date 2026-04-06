from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124DCpoBcdHeatLadderTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V124DCpoBcdHeatLadderTriageAnalyzer:
    def analyze(self) -> V124DCpoBcdHeatLadderTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "keep_balanced_ladder_frozen",
                "reason": "all_ladder_variants_only_trade_return_for_modest_drawdown_relief_without_beating_balanced_reference",
                "recommended_next_step": "stop_ladder_tuning_and_preserve_balanced_heat_reference_as_execution_default",
            },
            {
                "reviewer": "Tesla",
                "verdict": "keep_balanced_ladder_frozen",
                "reason": "no_variant_improves_objective_or_interval_outcome_over_balanced_heat_reference",
                "recommended_next_step": "treat_ladder_family_as_exhausted_under_current_heat_budget",
            },
            {
                "reviewer": "James",
                "verdict": "keep_balanced_ladder_frozen",
                "reason": "continued_ladder_tuning_is_same_dimension_optimization_with_no_new_edge",
                "recommended_next_step": "move_on_from_add_ladder_micro_tuning",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v124d_cpo_bcd_heat_ladder_triage_v1",
            "related_runs": ["V124B", "V124C", "V124D"],
            "authoritative_status": "keep_balanced_ladder_frozen",
            "majority_vote": {"keep_balanced_ladder_frozen": 3},
            "balanced_heat_reference_replay_facing_allowed": True,
            "alternative_ladder_replay_facing_allowed": False,
            "recommended_next_posture": "retain_balanced_heat_reference_as_only_live_add_budget_and_stop_same_family_ladder_tuning",
        }
        interpretation = [
            "V1.24D freezes the heat-aware add-ladder family after one full tuning cycle and interval compare.",
            "The conclusion is simple: smaller ladders can lower drawdown, but none of them beat the current balanced heat reference on the actual objective.",
            "This means the add-budget dimension is locally exhausted under the present heat framework.",
        ]
        return V124DCpoBcdHeatLadderTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124DCpoBcdHeatLadderTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124DCpoBcdHeatLadderTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124d_cpo_bcd_heat_ladder_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
