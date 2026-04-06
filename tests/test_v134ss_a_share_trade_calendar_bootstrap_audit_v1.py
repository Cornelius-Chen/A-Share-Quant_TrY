from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ss_a_share_trade_calendar_bootstrap_audit_v1 import (
    V134SSAShareTradeCalendarBootstrapAuditV1Analyzer,
)


def test_v134ss_trade_calendar_bootstrap_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SSAShareTradeCalendarBootstrapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["calendar_row_count"] > 1000
    assert report.summary["open_day_count"] > 500
    assert report.summary["coverage_start"] <= "2024-01-01"
    assert report.summary["coverage_end"] >= "2026-12-31"
    assert report.summary["today_calendar_state"] in {"trading_day", "non_trading_day"}


def test_v134ss_trade_calendar_bootstrap_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SSAShareTradeCalendarBootstrapAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["trade_calendar_registry"] == "materialized"
    assert rows["trade_calendar_coverage"] == "materialized"
    assert rows["today_calendar_state"] == "materialized"
