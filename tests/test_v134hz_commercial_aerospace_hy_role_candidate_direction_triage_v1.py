from pathlib import Path

from a_share_quant.strategy.v134hz_commercial_aerospace_hy_role_candidate_direction_triage_v1 import (
    V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Analyzer,
)


def test_v134hz_role_candidate_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HZCommercialAerospaceHYRoleCandidateDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_symbol_count"] == 5
    assert report.summary["hard_retained_count"] == 1
    directions = {row["candidate_group"]: row["direction"] for row in report.triage_rows}
    assert directions["hard_retained_role_seed"] == "keep_000547_as_the_only_hard_anchor_decoy_case_for_now"
    assert directions["capital_true_selection"] == "continue_blocked_until_role_candidates_are_better_separated"
