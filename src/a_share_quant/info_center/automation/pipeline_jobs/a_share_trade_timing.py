from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_trade_calendar_bootstrap_v1 import (
    MaterializeAShareTradeCalendarBootstrapV1,
)


def trading_day_state_approx(now_cn: datetime) -> str:
    return "trading_day_approx" if now_cn.weekday() < 5 else "non_trading_day_approx"


def session_phase_from_clock(now_cn: datetime) -> str:
    if now_cn.weekday() >= 5:
        return "non_trading_day"
    hm = now_cn.hour * 60 + now_cn.minute
    if hm < 9 * 60 + 15:
        return "pre_open"
    if hm < 9 * 60 + 25:
        return "opening_call_auction"
    if hm < 9 * 60 + 30:
        return "pre_continuous_auction_buffer"
    if hm < 11 * 60 + 30:
        return "morning_continuous_session"
    if hm < 13 * 60:
        return "lunch_break"
    if hm < 14 * 60 + 57:
        return "afternoon_continuous_session"
    if hm < 15 * 60:
        return "closing_call_auction"
    return "post_close"


def session_handling_mode(trading_day_state: str, session_phase: str) -> str:
    if trading_day_state in {"non_trading_day", "non_trading_day_approx"}:
        return "non_trading_day_watch_only"
    if session_phase in {"pre_open", "opening_call_auction", "pre_continuous_auction_buffer"}:
        return "pre_open_prepare_only"
    if session_phase in {"morning_continuous_session", "afternoon_continuous_session", "closing_call_auction"}:
        return "live_session_monitoring"
    if session_phase == "lunch_break":
        return "intraday_pause_hold_context"
    return "post_close_review_only"


def resolve_trade_timing(repo_root: Path, *, now_cn: datetime | None = None) -> dict[str, str]:
    if now_cn is None:
        now_cn = datetime.now(ZoneInfo("Asia/Shanghai"))
    try:
        trade_calendar = MaterializeAShareTradeCalendarBootstrapV1(repo_root).materialize()
        row_by_date = {row["cal_date"]: row for row in trade_calendar.rows}
        calendar_row = row_by_date.get(now_cn.date().isoformat())
        if calendar_row is None:
            trading_day_state = trading_day_state_approx(now_cn)
            session_phase_confidence = "approx_outside_trade_calendar_window"
        else:
            trading_day_state = "trading_day" if calendar_row["is_open"] == "1" else "non_trading_day"
            session_phase_confidence = "exact_with_trade_calendar"
    except Exception:
        trading_day_state = trading_day_state_approx(now_cn)
        session_phase_confidence = "approx_without_holiday_calendar"

    session_phase = (
        "non_trading_day"
        if trading_day_state in {"non_trading_day", "non_trading_day_approx"}
        else session_phase_from_clock(now_cn)
    )
    return {
        "trading_day_state": trading_day_state,
        "session_phase": session_phase,
        "session_phase_confidence": session_phase_confidence,
        "session_handling_mode": session_handling_mode(trading_day_state, session_phase),
    }
