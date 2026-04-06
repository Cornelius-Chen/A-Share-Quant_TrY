from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123PCpoMnoDailyResidualTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123PCpoMnoDailyResidualTriageAnalyzer:
    def analyze(self) -> V123PCpoMnoDailyResidualTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "candidate_only",
                "reason": "first_residual_downside_branch_with_stable_chronology_and_contained_false_positives_but_still_narrow",
                "recommended_next_step": "one_narrow_non_replay_attachment_audit_only_inside_held_pair_residual_context",
            },
            {
                "reviewer": "Tesla",
                "verdict": "candidate_only",
                "reason": "real_signal_on_residual_downside_subset_but_too_specific_to_300308_plus_300502_held_pair_context",
                "recommended_next_step": "non_replay_residual_revalidation_on_adjacent_drawdown_windows_only",
            },
            {
                "reviewer": "James",
                "verdict": "soft_component",
                "reason": "stable_enough_to_keep_but_context_too_narrow_for_full_candidate_budget",
                "recommended_next_step": "expand_only_within_held_pair_high_cash_residual_windows_before_any_upgrade",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123p_cpo_mno_daily_residual_triage_v1",
            "related_runs": ["V123M", "V123N", "V123O"],
            "branch_name": "held_pair_deterioration_score",
            "authoritative_status": "candidate_only",
            "majority_vote": {"candidate_only": 2, "soft_component": 1},
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "recommended_next_posture": "allow_only_non_replay_residual_revalidation_inside_held_pair_high_cash_context",
        }
        interpretation = [
            "V1.23P freezes the first residual daily downside branch after discovery, chronology audit, and boundary false-positive review.",
            "The branch is stronger than a pure explanatory layer because it survives chronology and keeps boundary false positives contained, but it remains tightly tied to the held 300308 plus 300502 high-cash carry context.",
            "The correct next step is narrow residual-context revalidation only, not replay-facing attachment and not broad family expansion.",
        ]
        return V123PCpoMnoDailyResidualTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123PCpoMnoDailyResidualTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123PCpoMnoDailyResidualTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123p_cpo_mno_daily_residual_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
