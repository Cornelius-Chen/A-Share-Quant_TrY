from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134st_a_share_ss_trade_calendar_direction_triage_v1 import (
    V134STAShareSSTradeCalendarDirectionTriageV1Analyzer,
)


def test_v134st_trade_calendar_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134STAShareSSTradeCalendarDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["calendar_row_count"] > 1000
    assert report.summary["today_calendar_state"] in {"trading_day", "non_trading_day"}
    assert (
        report.summary["authoritative_status"]
        == "prefer_trade_calendar_backed_trading_day_state_over_weekday_approximation"
    )


def test_v134st_trade_calendar_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134STAShareSSTradeCalendarDirectionTriageV1Analyzer(repo_root).analyze()
    components = {row["component"] for row in report.triage_rows}

    assert "status_surface" in components
    assert "session_phase_confidence" in components
    assert "fallback_branch" in components
