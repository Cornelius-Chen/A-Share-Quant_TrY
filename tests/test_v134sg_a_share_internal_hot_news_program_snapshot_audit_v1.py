from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sg_a_share_internal_hot_news_program_snapshot_audit_v1 import (
    V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer,
)


def test_v134sg_program_snapshot_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer(repo_root).analyze()

    assert report.summary["snapshot_row_count"] == 1
    assert report.summary["risk_feed_row_count"] >= 0
    assert report.summary["opportunity_feed_row_count"] >= 0
    assert report.summary["session_handling_mode"] in {
        "non_trading_day_watch_only",
        "pre_open_prepare_only",
        "live_session_monitoring",
        "intraday_pause_hold_context",
        "post_close_review_only",
        "unknown",
    }
    assert report.summary["risk_consumer_gate"] in {
        "allow_live_risk_guardrail",
        "prepare_risk_guardrail_before_open",
        "hold_risk_context_during_break",
        "review_risk_after_close",
        "watch_risk_non_trading_day",
        "unknown",
    }
    assert report.summary["opportunity_consumer_gate"] in {
        "allow_live_opportunity_routing",
        "allow_live_board_watch_only",
        "prepare_opportunity_watch_before_open",
        "hold_opportunity_context_during_break",
        "review_opportunity_after_close",
        "watch_opportunity_non_trading_day",
        "unknown",
    }
    assert report.summary["snapshot_consumer_gate_mode"] in {
        "live_session_consumer_routing",
        "pre_open_consumer_prepare",
        "intraday_break_context_hold",
        "post_close_consumer_review",
        "non_trading_day_watch_only",
    }


def test_v134sg_program_snapshot_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_snapshot"] == "read_ready_internal_only"
    assert rows["risk_snapshot"] == "materialized"
    assert rows["timing_snapshot"] == "materialized"
    assert rows["risk_consumer_gate"] == "materialized"
    assert rows["opportunity_consumer_gate"] == "materialized"
