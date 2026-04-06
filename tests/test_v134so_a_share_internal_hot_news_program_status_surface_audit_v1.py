from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134so_a_share_internal_hot_news_program_status_surface_audit_v1 import (
    V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer,
)


def test_v134so_program_status_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["status_row_count"] == 1
    assert report.summary["program_health_state"] in {"healthy_internal_only", "degraded"}
    assert report.summary["needs_attention"] in {"true", "false"}
    assert report.summary["trading_day_state"] in {
        "trading_day",
        "non_trading_day",
        "trading_day_approx",
        "non_trading_day_approx",
    }
    assert report.summary["session_phase"] in {
        "pre_open",
        "opening_call_auction",
        "pre_continuous_auction_buffer",
        "morning_continuous_session",
        "lunch_break",
        "afternoon_continuous_session",
        "closing_call_auction",
        "post_close",
        "non_trading_day",
    }
    assert report.summary["session_phase_confidence"] in {
        "exact_with_trade_calendar",
        "approx_without_holiday_calendar",
        "approx_outside_trade_calendar_window",
    }
    assert report.summary["program_consumer_gate_mode"] in {
        "allow_live_session_routing",
        "prepare_only_before_open",
        "hold_context_during_break",
        "review_only_after_close",
        "watch_only_non_trading_day",
        "degraded_watch_until_refresh",
        "stale_block_until_refresh",
    }
    assert report.summary["program_driver_action_mode"] in {
        "watch_only",
        "prepare",
        "live_route",
        "break_hold",
        "review",
        "degraded_watch",
        "stale_block",
    }
    assert report.summary["freshness_state"] in {"fresh", "warming_stale", "stale"}
    assert report.summary["heartbeat_timeout_state"] in {"within_timeout", "near_timeout", "timed_out"}
    assert report.summary["stale_alert_level"] in {"none", "warning", "critical"}
    assert report.summary["force_refresh"] in {"true", "false"}


def test_v134so_program_status_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_status_surface"] == "read_ready_internal_only"
    assert rows["program_health"] == "materialized"
    assert rows["session_gate"] == "materialized"
    assert rows["session_confidence_gate"] == "materialized"
    assert rows["program_consumer_gate"] == "materialized"
    assert rows["program_driver_action"] == "materialized"
    assert rows["freshness_gate"] == "materialized"
    assert rows["heartbeat_timeout_gate"] == "materialized"
    assert rows["stale_alert_gate"] == "materialized"
