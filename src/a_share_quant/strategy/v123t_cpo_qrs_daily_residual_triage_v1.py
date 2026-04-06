from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123TCpoQrsDailyResidualTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123TCpoQrsDailyResidualTriageAnalyzer:
    def analyze(self) -> V123TCpoQrsDailyResidualTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "soft_component",
                "reason": "stable_across_cash_floors_but_diffuse_inside_interval_so_not_clean_enough_for_candidate_budget",
                "recommended_next_step": "keep_as_residual_downside_penalty_only",
            },
            {
                "reviewer": "Tesla",
                "verdict": "soft_component",
                "reason": "chronology_and_boundary_hold_but_core_focus_fails",
                "recommended_next_step": "do_not_expand_beyond_residual_context",
            },
            {
                "reviewer": "James",
                "verdict": "soft_component",
                "reason": "stable_residual_signal_but_too_diffuse_inside_interval_to_keep_candidate_budget",
                "recommended_next_step": "stop_treating_it_as_candidate_and_keep_only_as_residual_soft_overlay",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123t_cpo_qrs_daily_residual_triage_v1",
            "related_runs": ["V123Q", "V123R", "V123S"],
            "branch_name": "held_pair_deterioration_score",
            "authoritative_status": "soft_component",
            "majority_vote": {"soft_component": 3},
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "recommended_next_posture": "retain_only_as_residual_downside_soft_penalty_inside_held_pair_high_cash_context",
        }
        interpretation = [
            "V1.23T freezes the residual downside branch after cash-floor sensitivity, core-stress concentration, and granular boundary review.",
            "The branch survives chronology and boundary containment, but it fails the stronger test of focusing on the deepest stress core inside the residual interval.",
            "All three reviewers therefore demote it to soft_component: still useful inside the narrow residual context, but no longer worthy of candidate budget.",
        ]
        return V123TCpoQrsDailyResidualTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123TCpoQrsDailyResidualTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123TCpoQrsDailyResidualTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123t_cpo_qrs_daily_residual_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
