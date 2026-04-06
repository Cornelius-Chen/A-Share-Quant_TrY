from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rc_a_share_internal_hot_news_trading_guidance_audit_v1 import (
    V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer,
)


def test_v134rc_internal_hot_news_guidance_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["guidance_row_count"] > 0
    assert report.summary["risk_event_count"] >= 0
    assert report.summary["guidance_event_count"] >= 0
    assert report.summary["trigger_event_count"] >= 0
    assert report.summary["market_guidance_row_count"] >= 0
    assert report.summary["board_signal_row_count"] >= 0
    assert report.summary["risk_queue_row_count"] >= 0
    assert report.summary["decision_signal_row_count"] >= 0


def test_v134rc_internal_hot_news_guidance_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["trading_guidance_surface"] == "read_ready_internal_only"
    assert rows["board_guidance_summary"] == "materialized"
    assert rows["market_guidance_surface"] == "read_ready_internal_only"
    assert rows["board_signal_surface"] == "read_ready_internal_only"
    assert rows["risk_queue_surface"] == "read_ready_internal_only"
    assert rows["decision_signal_surface"] == "read_ready_internal_only"
