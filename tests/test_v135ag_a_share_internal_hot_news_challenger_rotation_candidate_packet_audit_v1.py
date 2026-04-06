from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ag_a_share_internal_hot_news_challenger_rotation_candidate_packet_audit_v1 import (
    V135AGAShareInternalHotNewsChallengerRotationCandidatePacketAuditV1Analyzer,
)


def test_v135ag_challenger_rotation_candidate_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AGAShareInternalHotNewsChallengerRotationCandidatePacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_top_opportunity_theme"] not in {"", "none"}
    assert report.summary["challenger_top_opportunity_theme"] not in {"", "none", report.summary["current_top_opportunity_theme"]}
    assert report.summary["current_top_watch_symbol"]
    assert report.summary["challenger_top_watch_symbol"] != report.summary["current_top_watch_symbol"]


def test_v135ag_challenger_rotation_candidate_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AGAShareInternalHotNewsChallengerRotationCandidatePacketAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 4
