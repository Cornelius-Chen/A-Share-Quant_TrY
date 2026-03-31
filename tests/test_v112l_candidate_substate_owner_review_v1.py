from pathlib import Path

from a_share_quant.strategy.v112l_candidate_substate_owner_review_v1 import (
    V112LCandidateSubstateOwnerReviewAnalyzer,
    load_json_report,
)


def test_v112l_candidate_substate_owner_review_v1_preserves_two_review_only_rows() -> None:
    result = V112LCandidateSubstateOwnerReviewAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112l_phase_charter_v1.json")),
        candidate_substate_draft_payload=load_json_report(Path("reports/analysis/v112k_candidate_substate_draft_v1.json")),
    )
    assert result.summary["preserved_review_only_count"] == 2
    assert result.summary["mixed_inner_drafting_target_count"] == 1
    assert result.summary["formal_label_split_now"] is False
