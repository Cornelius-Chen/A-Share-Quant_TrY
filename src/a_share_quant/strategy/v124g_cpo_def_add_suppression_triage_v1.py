from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124GCpoDefAddSuppressionTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V124GCpoDefAddSuppressionTriageAnalyzer:
    def analyze(self) -> V124GCpoDefAddSuppressionTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "keep_add_suppression_blocked",
                "reason": "branch_is_inactive_not_merely_weak_because_overlap_with_real_riskoff_inside_hot_states_is_zero",
                "recommended_next_step": "stop_this_family_instead_of_tuning_thresholds_or_heat_gates",
            },
            {
                "reviewer": "Tesla",
                "verdict": "keep_add_suppression_blocked",
                "reason": "suppressed_add_count_zero_and_rows_over_threshold_zero_mean_no_execution_surface_exists",
                "recommended_next_step": "treat_as_non-starter_and_do_not_spend_more_execution_budget_here",
            },
            {
                "reviewer": "James",
                "verdict": "keep_add_suppression_blocked",
                "reason": "there_is_no_real_trigger_overlap_so_further_work_would_be_empty_tuning",
                "recommended_next_step": "close_the_family_and_move_to_the_next_real_control_problem",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v124g_cpo_def_add_suppression_triage_v1",
            "related_runs": ["V124D", "V124E", "V124F"],
            "authoritative_status": "keep_add_suppression_blocked",
            "majority_vote": {"keep_add_suppression_blocked": 3},
            "replay_facing_allowed": False,
            "recommended_next_posture": "keep_balanced_heat_reference_as_only_live_execution_control_and_stop_add_suppression_family",
        }
        interpretation = [
            "V1.24G freezes the add-suppression branch after the heat-ladder freeze and overlap audit.",
            "The branch is blocked not because it is mildly weak, but because it has no real execution surface in the current sample: zero threshold overlap and zero suppressed adds.",
            "That makes further tuning wasteful rather than cautious.",
        ]
        return V124GCpoDefAddSuppressionTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124GCpoDefAddSuppressionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124GCpoDefAddSuppressionTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124g_cpo_def_add_suppression_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
