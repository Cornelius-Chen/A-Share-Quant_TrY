from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zm_a_share_internal_hot_news_accepted_rotation_candidate_packet_audit_v1 import (
    V134ZMAShareInternalHotNewsAcceptedRotationCandidatePacketAuditV1Analyzer,
)


def test_v134zm_accepted_rotation_candidate_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZMAShareInternalHotNewsAcceptedRotationCandidatePacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_top_opportunity_theme"]
    assert report.summary["accepted_top_opportunity_theme"]


def test_v134zm_accepted_rotation_candidate_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZMAShareInternalHotNewsAcceptedRotationCandidatePacketAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 4
