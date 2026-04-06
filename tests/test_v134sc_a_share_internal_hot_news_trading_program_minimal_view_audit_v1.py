from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sc_a_share_internal_hot_news_trading_program_minimal_view_audit_v1 import (
    V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer,
)


def test_v134sc_trading_program_minimal_view_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["minimal_view_row_count"] > 0
    assert report.summary["risk_guardrail_count"] >= 0
    assert report.summary["top_down_guidance_count"] >= 0
    assert report.summary["board_watch_trigger_count"] >= 0
    assert report.summary["symbol_focus_available_count"] >= 0
    assert report.summary["session_handling_mode"] in {
        "non_trading_day_watch_only",
        "pre_open_prepare_only",
        "live_session_monitoring",
        "intraday_pause_hold_context",
        "post_close_review_only",
    }


def test_v134sc_trading_program_minimal_view_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["minimal_consumer_view"] == "read_ready_internal_only"
    assert rows["risk_guardrail"] == "materialized"
    assert rows["timing_gate"] == "materialized"
