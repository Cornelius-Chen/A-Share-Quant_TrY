from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aq_a_share_internal_hot_news_focus_governance_tension_packet_audit_v1 import (
    V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer,
)


def test_v135aq_focus_governance_tension_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["current_primary_rank"] >= 1
    assert report.summary["incumbent_is_leader"] in {"true", "false"}
    assert report.summary["tension_priority"] in {"p1", "p2", "p3"}


def test_v135aq_focus_governance_tension_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["incumbent_is_leader"] in {"true", "false"}
    assert rows["tension_priority"] in {"p1", "p2", "p3"}
