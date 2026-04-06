from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134se_a_share_internal_hot_news_program_split_feeds_audit_v1 import (
    V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer,
)


def test_v134se_program_split_feeds_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer(repo_root).analyze()

    assert report.summary["risk_feed_row_count"] >= 0
    assert report.summary["opportunity_feed_row_count"] >= 0
    assert report.summary["critical_risk_count"] >= 0
    assert report.summary["critical_opportunity_count"] >= 0
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
    assert report.summary["top_opportunity_theme_slug"] != ""
    assert float(report.summary["top_opportunity_focus_total_score"]) >= 0.0


def test_v134se_program_split_feeds_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_risk_feed"] == "read_ready_internal_only"
    assert rows["program_opportunity_feed"] == "read_ready_internal_only"
    assert rows["timing_gate"] == "materialized"
    assert rows["risk_consumer_gate"] == "materialized"
    assert rows["opportunity_consumer_gate"] == "materialized"
    assert rows["opportunity_focus_scoring"] == "materialized"
