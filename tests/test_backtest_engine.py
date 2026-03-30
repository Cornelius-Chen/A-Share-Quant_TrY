from __future__ import annotations

from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.models import DailyBar, Signal


def build_bar(
    trade_date: str,
    symbol: str,
    open_price: float,
    close_price: float,
    pre_close: float,
) -> DailyBar:
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        open=open_price,
        high=max(open_price, close_price),
        low=min(open_price, close_price),
        close=close_price,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=pre_close,
        adjust_factor=1.0,
        listed_days=200,
    )


def test_engine_executes_next_day_and_generates_summary() -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, 10.2, 10.0),
        build_bar("2025-01-03", "AAA", 10.1, 10.6, 10.2),
        build_bar("2025-01-06", "AAA", 10.7, 10.8, 10.6),
    ]
    signals = [
        Signal(trade_date=date(2025, 1, 2), symbol="AAA", action="buy", quantity=100),
        Signal(trade_date=date(2025, 1, 3), symbol="AAA", action="sell", quantity=100),
    ]

    engine = BacktestEngine(
        initial_cash=100_000,
        cost_model=CostModel(
            commission_bps=0.0,
            stamp_tax_bps=0.0,
            transfer_fee_bps=0.0,
            exchange_handling_bps=0.0,
            regulatory_fee_bps=0.0,
            min_commission=0.0,
        ),
        limit_model=LimitModel(daily_limit_pct=0.10, epsilon=0.0001),
    )
    result = engine.run(bars, signals)

    assert len(result.fills) == 2
    assert result.fills[0].trade_date == date(2025, 1, 3)
    assert result.fills[1].trade_date == date(2025, 1, 6)
    assert result.summary["closed_trade_count"] == 1
    assert result.summary["total_return"] > 0


def test_engine_blocks_sell_without_position() -> None:
    bars = [
        build_bar("2025-01-02", "AAA", 10.0, 10.2, 10.0),
        build_bar("2025-01-03", "AAA", 10.1, 10.6, 10.2),
    ]
    signals = [
        Signal(trade_date=date(2025, 1, 2), symbol="AAA", action="sell", quantity=100),
    ]

    engine = BacktestEngine(
        initial_cash=100_000,
        cost_model=CostModel(
            commission_bps=0.0,
            stamp_tax_bps=0.0,
            transfer_fee_bps=0.0,
            exchange_handling_bps=0.0,
            regulatory_fee_bps=0.0,
            min_commission=0.0,
        ),
        limit_model=LimitModel(daily_limit_pct=0.10, epsilon=0.0001),
    )
    result = engine.run(bars, signals)

    assert len(result.fills) == 0
    assert result.summary["rejected_signal_count"] == 1
