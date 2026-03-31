from pathlib import Path

from a_share_quant.strategy.v112m_mixed_stall_inner_draft_v1 import (
    V112MMixedStallInnerDraftAnalyzer,
    load_json_report,
)


def test_v112m_mixed_stall_inner_draft_v1_preserves_two_inner_candidates() -> None:
    result = V112MMixedStallInnerDraftAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112m_phase_charter_v1.json")),
        pilot_dataset_payload=load_json_report(Path("reports/analysis/v112b_pilot_dataset_freeze_v1.json")),
        prior_owner_review_payload=load_json_report(Path("reports/analysis/v112l_candidate_substate_owner_review_v1.json")),
    )
    assert result.summary["preservable_review_only_inner_candidate_count"] == 2
    assert result.summary["unresolved_inner_residue_count"] == 1
    assert result.summary["formal_label_split_now"] is False
