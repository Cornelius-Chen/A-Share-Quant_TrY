from a_share_quant.strategy.v123g_cpo_def_1min_downside_attachment_triage_v1 import (
    V123GCpoDef1MinDownsideAttachmentTriageAnalyzer,
)


def test_v123g_freezes_attachment_blocked() -> None:
    result = V123GCpoDef1MinDownsideAttachmentTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "keep_attachment_blocked"
    assert result.summary["same_plane_attachment_allowed"] is False

