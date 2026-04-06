from pathlib import Path

from a_share_quant.strategy.v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1 import (
    V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer,
)


def test_v134hy_event_attention_role_candidate_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_symbol_count"] == 5
    assert report.summary["hard_retained_count"] == 1
    assert report.summary["soft_candidate_count"] == 4
    roles = {row["symbol"]: row["candidate_role"] for row in report.candidate_rows}
    assert roles["000547"] == "attention_anchor_and_attention_decoy"
    assert roles["603601"] == "crowded_attention_carrier_candidate"
    assert roles["002361"] == "crowding_only_role_candidate"
    assert roles["300342"] == "outlier_breakout_concentration_candidate"
    assert roles["301306"] == "high_beta_attention_follow_candidate"
