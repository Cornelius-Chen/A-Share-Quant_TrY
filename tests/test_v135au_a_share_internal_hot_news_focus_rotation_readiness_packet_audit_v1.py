from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135au_a_share_internal_hot_news_focus_rotation_readiness_packet_audit_v1 import (
    V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer,
)


def test_v135au_focus_rotation_readiness_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["current_primary_rank"] >= 1
    assert report.summary["rotation_readiness_priority"] in {"p1", "p2", "p3"}


def test_v135au_focus_rotation_readiness_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AUAShareInternalHotNewsFocusRotationReadinessPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["rotation_readiness_priority"] in {"p1", "p2", "p3"}
