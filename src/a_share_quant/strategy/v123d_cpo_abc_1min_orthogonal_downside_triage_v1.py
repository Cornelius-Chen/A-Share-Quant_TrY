from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123DCpoAbc1MinOrthogonalDownsideTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123DCpoAbc1MinOrthogonalDownsideTriageAnalyzer:
    def analyze(self) -> V123DCpoAbc1MinOrthogonalDownsideTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "soft_component",
                "reason": "alive_but_too_weak_for_candidate_rule_even_if_orthogonal",
                "recommended_next_step": "standalone_soft_component_only_with_non_replay_increment_audit",
            },
            {
                "reviewer": "Tesla",
                "verdict": "soft_component",
                "reason": "orthogonal_and_alive_but_not_strong_enough_for_candidate_only",
                "recommended_next_step": "non_replay_integration_value_audit_only",
            },
            {
                "reviewer": "James",
                "verdict": "candidate_only",
                "reason": "stable_enough_across_time_and_symbol_to_stay_alive",
                "recommended_next_step": "same_plane_non_replay_integration_audit_against_downside_failure",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123d_cpo_abc_1min_orthogonal_downside_triage_v1",
            "related_runs": ["V123A", "V123B", "V123C"],
            "branch_name": "gap_exhaustion_stall_score",
            "authoritative_status": "soft_component",
            "majority_vote": {"soft_component": 2, "candidate_only": 1},
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "recommended_next_posture": "allow_only_one_non_replay_same_plane_integration_audit_against_downside_failure",
        }
        interpretation = [
            "V1.23D freezes the new orthogonal 1-minute downside branch after scan, time-split, and symbol-holdout review.",
            "The branch is better than the old recent 1-minute downside line on orthogonality and transfer, but still not strong enough to become a replay-facing candidate.",
            "The correct next step is one non-replay same-plane integration audit against downside_failure, not promotion and not family expansion.",
        ]
        return V123DCpoAbc1MinOrthogonalDownsideTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123DCpoAbc1MinOrthogonalDownsideTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123DCpoAbc1MinOrthogonalDownsideTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123d_cpo_abc_1min_orthogonal_downside_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

