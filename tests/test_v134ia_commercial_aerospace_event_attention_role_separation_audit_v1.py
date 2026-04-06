from pathlib import Path

from a_share_quant.strategy.v134ia_commercial_aerospace_event_attention_role_separation_audit_v1 import (
    V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer,
)


def test_v134ia_event_attention_role_separation_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["soft_candidate_count"] == 4
    roles = {row["symbol"]: row["separated_role"] for row in report.separated_rows}
    assert roles["603601"] == "event_backed_attention_carrier_candidate"
    assert roles["002361"] == "non_anchor_crowded_concentration_candidate"
    assert roles["300342"] == "non_anchor_outlier_breakout_candidate"
    assert roles["301306"] == "event_backed_high_beta_follow_candidate"
    assert report.summary["event_backed_attention_carrier_count"] == 1
