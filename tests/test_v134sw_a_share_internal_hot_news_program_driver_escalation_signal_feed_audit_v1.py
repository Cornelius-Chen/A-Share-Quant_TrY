from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sw_a_share_internal_hot_news_program_driver_escalation_signal_feed_audit_v1 import (
    V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer,
)


def test_v134sw_driver_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_feed_mode"] in {"interrupt", "elevate_attention", "passive_polling"}
    assert report.summary["interrupt_required"] in {"true", "false"}
    assert report.summary["alert_state"] in {
        "high_priority_driver_escalation",
        "elevated_driver_escalation",
        "no_driver_escalation",
    }


def test_v134sw_driver_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["driver_escalation_signal_feed"] == "read_ready_internal_only"
    assert rows["signal_feed_mode"] == "materialized"
    assert rows["interrupt_required"] == "materialized"
    assert rows["alert_state"] == "materialized"
