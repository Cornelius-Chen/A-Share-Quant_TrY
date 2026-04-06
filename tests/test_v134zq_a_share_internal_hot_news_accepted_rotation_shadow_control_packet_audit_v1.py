from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zq_a_share_internal_hot_news_accepted_rotation_shadow_control_packet_audit_v1 import (
    V134ZQAShareInternalHotNewsAcceptedRotationShadowControlPacketAuditV1Analyzer,
)


def test_v134zq_accepted_rotation_shadow_control_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZQAShareInternalHotNewsAcceptedRotationShadowControlPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_top_opportunity_theme"]
    assert report.summary["shadow_top_opportunity_theme"]


def test_v134zq_accepted_rotation_shadow_control_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZQAShareInternalHotNewsAcceptedRotationShadowControlPacketAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 4
