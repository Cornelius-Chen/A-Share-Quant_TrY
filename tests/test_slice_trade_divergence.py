from __future__ import annotations

from datetime import date

from a_share_quant.strategy.slice_trade_divergence import SliceTradeDivergenceAnalyzer


class _Trade:
    def __init__(self, symbol: str, entry_date: date, exit_date: date, pnl: float, holding_days: int) -> None:
        self.symbol = symbol
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.quantity = 100
        self.entry_price = 10.0
        self.exit_price = 11.0
        self.fees = 1.0
        self.pnl = pnl
        self.holding_days = holding_days


class _BacktestResult:
    def __init__(self, trades: list[_Trade]) -> None:
        self.closed_trades = trades


class _Result:
    def __init__(self, trades: list[_Trade]) -> None:
        self.backtest_result = _BacktestResult(trades)


def test_symbol_summary_rows_identify_negative_pnl_delta() -> None:
    analyzer = SliceTradeDivergenceAnalyzer()
    incumbent = _Result([_Trade("000001", date(2024, 1, 2), date(2024, 1, 5), 100.0, 3)])
    challenger = _Result([_Trade("000001", date(2024, 1, 2), date(2024, 1, 5), 70.0, 3)])

    rows = analyzer._symbol_summary_rows(
        strategy_name="mainline_trend_a",
        incumbent_result=incumbent,
        challenger_result=challenger,
    )

    assert rows[0]["symbol"] == "000001"
    assert rows[0]["pnl_delta"] == -30.0
