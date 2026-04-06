from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124ACpoYzaHeatConditionedRiskoffTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V124ACpoYzaHeatConditionedRiskoffTriageAnalyzer:
    def analyze(self) -> V124ACpoYzaHeatConditionedRiskoffTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "shadow_only_not_promotable",
                "reason": "narrow_line_is_no_longer_catastrophically_over_defensive_but_still_loses_main_objective_to_balanced_heat_reference",
                "recommended_next_step": "retain_only_as_shadow_comparison_and_stop_execution_promotion_attempts",
            },
            {
                "reviewer": "Tesla",
                "verdict": "shadow_only_not_promotable",
                "reason": "drawdown_improves_materially_but_return_drop_is_still_too_large_for_candidate_execution_path",
                "recommended_next_step": "keep_as_defensive_shadow_variant_without_attaching_to_live_execution_stack",
            },
            {
                "reviewer": "James",
                "verdict": "shadow_only_not_promotable",
                "reason": "narrow_execution_line_is_observable_and_useful_but_still_not_good_enough_to_replace_or_join_heat_primary_execution",
                "recommended_next_step": "freeze_as_shadow_only_and_move_on_from_this_family",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v124a_cpo_yza_heat_conditioned_riskoff_triage_v1",
            "related_runs": ["V123Y", "V123Z", "V124A"],
            "authoritative_status": "shadow_only_not_promotable",
            "majority_vote": {"shadow_only_not_promotable": 3},
            "heat_replay_facing_allowed": True,
            "heat_conditioned_riskoff_replay_facing_allowed": False,
            "recommended_next_posture": "keep_balanced_heat_reference_as_only_replay_facing_control_and_archive_narrow_riskoff_as_shadow_defensive_variant",
        }
        interpretation = [
            "V1.24A freezes the narrow heat-conditioned risk-off verdict after one execution retry cycle.",
            "The retry succeeded in proving that broad risk-off was not the only possible shape, because conditional risk-off no longer collapses the curve to baseline-like returns.",
            "But it still cannot beat the balanced heat reference on the main tradeoff, so it must stop at shadow-only and not consume more execution-promotion budget.",
        ]
        return V124ACpoYzaHeatConditionedRiskoffTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124ACpoYzaHeatConditionedRiskoffTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124ACpoYzaHeatConditionedRiskoffTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124a_cpo_yza_heat_conditioned_riskoff_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
