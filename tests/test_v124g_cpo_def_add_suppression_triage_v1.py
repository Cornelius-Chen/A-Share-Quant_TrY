from a_share_quant.strategy.v124g_cpo_def_add_suppression_triage_v1 import (
    V124GCpoDefAddSuppressionTriageAnalyzer,
)


def test_v124g_add_suppression_triage_blocks_branch() -> None:
    result = V124GCpoDefAddSuppressionTriageAnalyzer().analyze()

    assert result.summary["authoritative_status"] == "keep_add_suppression_blocked"
    assert result.summary["majority_vote"]["keep_add_suppression_blocked"] == 3
    assert result.summary["replay_facing_allowed"] is False
