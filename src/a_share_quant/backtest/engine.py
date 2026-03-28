from __future__ import annotations

from collections import defaultdict
from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.backtest.metrics import build_summary
from a_share_quant.common.models import (
    BacktestResult,
    ClosedTrade,
    DailyBar,
    EquityPoint,
    Fill,
    Position,
    Signal,
)


class BacktestEngine:
    """A minimal daily-bar backtest engine with next-day execution and T+1 sale constraints."""

    def __init__(
        self,
        *,
        initial_cash: float,
        cost_model: CostModel,
        limit_model: LimitModel,
        price_field: str = "open",
    ) -> None:
        self.initial_cash = initial_cash
        self.cost_model = cost_model
        self.limit_model = limit_model
        self.price_field = price_field

    def run(self, bars: list[DailyBar], signals: list[Signal]) -> BacktestResult:
        bars_by_symbol = self._index_bars_by_symbol(bars)
        bars_by_date = self._index_bars_by_date(bars)
        scheduled = self._schedule_signals(bars_by_symbol, signals)

        cash = self.initial_cash
        positions: dict[str, Position] = {}
        entry_tracker: dict[str, tuple[date, float]] = {}
        fills: list[Fill] = []
        closed_trades: list[ClosedTrade] = []
        rejected: list[str] = []
        equity_curve: list[EquityPoint] = []

        for trade_date in sorted(bars_by_date):
            intents = scheduled.get(trade_date, [])
            intents.sort(key=lambda item: 0 if item[0].action == "sell" else 1)
            for signal, bar in intents:
                price = getattr(bar, self.price_field)
                if not self.limit_model.can_fill(signal.action, bar, price):
                    rejected.append(
                        f"{signal.trade_date}:{signal.symbol}:{signal.action}:blocked_by_limit_model"
                    )
                    continue

                if signal.action == "buy":
                    buy_cash = price * signal.quantity
                    buy_fees = self.cost_model.calculate(buy_cash, signal.action)
                    total_cash_needed = buy_cash + buy_fees
                    if total_cash_needed > cash:
                        rejected.append(
                            f"{signal.trade_date}:{signal.symbol}:buy:insufficient_cash"
                        )
                        continue

                    cash -= total_cash_needed
                    position = positions.get(signal.symbol, Position(symbol=signal.symbol))
                    new_quantity = position.quantity + signal.quantity
                    new_average_cost = (
                        position.average_cost * position.quantity + total_cash_needed
                    ) / new_quantity
                    positions[signal.symbol] = Position(
                        symbol=signal.symbol,
                        quantity=new_quantity,
                        average_cost=new_average_cost,
                        last_buy_date=bar.trade_date,
                    )
                    entry_tracker.setdefault(signal.symbol, (bar.trade_date, price))
                    fills.append(
                        Fill(
                            trade_date=bar.trade_date,
                            symbol=signal.symbol,
                            action=signal.action,
                            quantity=signal.quantity,
                            price=price,
                            fees=buy_fees,
                        )
                    )
                    continue

                if signal.action == "sell":
                    position = positions.get(signal.symbol)
                    if position is None or position.quantity < signal.quantity:
                        rejected.append(
                            f"{signal.trade_date}:{signal.symbol}:sell:no_position"
                        )
                        continue
                    if position.last_buy_date is not None and bar.trade_date <= position.last_buy_date:
                        rejected.append(
                            f"{signal.trade_date}:{signal.symbol}:sell:t_plus_one_block"
                        )
                        continue

                    sell_cash = price * signal.quantity
                    sell_fees = self.cost_model.calculate(sell_cash, signal.action)
                    cash += sell_cash - sell_fees
                    fills.append(
                        Fill(
                            trade_date=bar.trade_date,
                            symbol=signal.symbol,
                            action=signal.action,
                            quantity=signal.quantity,
                            price=price,
                            fees=sell_fees,
                        )
                    )

                    entry_date, entry_price = entry_tracker.get(
                        signal.symbol,
                        (bar.trade_date, position.average_cost),
                    )
                    gross_pnl = (price - position.average_cost) * signal.quantity
                    closed_trades.append(
                        ClosedTrade(
                            symbol=signal.symbol,
                            entry_date=entry_date,
                            exit_date=bar.trade_date,
                            quantity=signal.quantity,
                            entry_price=entry_price,
                            exit_price=price,
                            fees=sell_fees,
                            pnl=gross_pnl - sell_fees,
                            holding_days=(bar.trade_date - entry_date).days,
                        )
                    )

                    remaining_qty = position.quantity - signal.quantity
                    if remaining_qty == 0:
                        positions.pop(signal.symbol, None)
                        entry_tracker.pop(signal.symbol, None)
                    else:
                        positions[signal.symbol] = Position(
                            symbol=signal.symbol,
                            quantity=remaining_qty,
                            average_cost=position.average_cost,
                            last_buy_date=position.last_buy_date,
                        )
                    continue

                rejected.append(f"{signal.trade_date}:{signal.symbol}:{signal.action}:unsupported")

            equity = cash
            for symbol, position in positions.items():
                mark_bar = bars_by_date[trade_date].get(symbol)
                if mark_bar is None:
                    continue
                equity += mark_bar.close * position.quantity
            equity_curve.append(EquityPoint(trade_date=trade_date, equity=equity, cash=cash))

        result = BacktestResult(
            fills=fills,
            closed_trades=closed_trades,
            equity_curve=equity_curve,
            rejected_signals=rejected,
            summary={},
        )
        result.summary = build_summary(self.initial_cash, result)
        return result

    def _index_bars_by_symbol(self, bars: list[DailyBar]) -> dict[str, list[DailyBar]]:
        indexed: dict[str, list[DailyBar]] = defaultdict(list)
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            indexed[bar.symbol].append(bar)
        return indexed

    def _index_bars_by_date(self, bars: list[DailyBar]) -> dict[date, dict[str, DailyBar]]:
        indexed: dict[date, dict[str, DailyBar]] = defaultdict(dict)
        for bar in bars:
            indexed[bar.trade_date][bar.symbol] = bar
        return indexed

    def _schedule_signals(
        self,
        bars_by_symbol: dict[str, list[DailyBar]],
        signals: list[Signal],
    ) -> dict[date, list[tuple[Signal, DailyBar]]]:
        scheduled: dict[date, list[tuple[Signal, DailyBar]]] = defaultdict(list)
        for signal in sorted(signals, key=lambda item: (item.trade_date, item.symbol, item.action)):
            next_bar = self._find_next_bar(signal, bars_by_symbol.get(signal.symbol, []))
            if next_bar is None:
                continue
            scheduled[next_bar.trade_date].append((signal, next_bar))
        return scheduled

    def _find_next_bar(self, signal: Signal, bars: list[DailyBar]) -> DailyBar | None:
        for bar in bars:
            if bar.trade_date > signal.trade_date:
                return bar
        return None
