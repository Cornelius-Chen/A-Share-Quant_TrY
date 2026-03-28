from __future__ import annotations

from a_share_quant.common.models import BacktestResult, ClosedTrade, EquityPoint, MainlineWindow


def total_return(initial_cash: float, equity_curve: list[EquityPoint]) -> float:
    if not equity_curve:
        return 0.0
    return equity_curve[-1].equity / initial_cash - 1.0


def max_drawdown(equity_curve: list[EquityPoint]) -> float:
    if not equity_curve:
        return 0.0
    peak = equity_curve[0].equity
    worst = 0.0
    for point in equity_curve:
        peak = max(peak, point.equity)
        if peak <= 0.0:
            continue
        drawdown = point.equity / peak - 1.0
        worst = min(worst, drawdown)
    return abs(worst)


def win_rate(closed_trades: list[ClosedTrade]) -> float:
    if not closed_trades:
        return 0.0
    wins = sum(1 for trade in closed_trades if trade.pnl > 0.0)
    return wins / len(closed_trades)


def payoff_ratio(closed_trades: list[ClosedTrade]) -> float | str:
    wins = [trade.pnl for trade in closed_trades if trade.pnl > 0.0]
    losses = [abs(trade.pnl) for trade in closed_trades if trade.pnl < 0.0]
    if wins and not losses:
        return "inf"
    if not wins or not losses:
        return 0.0
    return (sum(wins) / len(wins)) / (sum(losses) / len(losses))


def mainline_capture_ratio(
    closed_trades: list[ClosedTrade],
    windows: list[MainlineWindow],
) -> float:
    if not windows:
        return 0.0

    total_capturable = sum(max(window.capturable_return, 0.0) for window in windows)
    if total_capturable <= 0.0:
        return 0.0

    captured = sum(_window_capture_ratio(closed_trades, window) * max(window.capturable_return, 0.0) for window in windows)
    return captured / total_capturable


def missed_mainline_count(
    closed_trades: list[ClosedTrade],
    windows: list[MainlineWindow],
    *,
    min_effective_capture: float = 0.20,
) -> int:
    missed = 0
    for window in windows:
        if _window_capture_ratio(closed_trades, window) < min_effective_capture:
            missed += 1
    return missed


def mainline_window_breakdown(
    closed_trades: list[ClosedTrade],
    windows: list[MainlineWindow],
    *,
    min_effective_capture: float = 0.20,
) -> list[dict[str, object]]:
    breakdown: list[dict[str, object]] = []
    for window in windows:
        capture_ratio = _window_capture_ratio(closed_trades, window)
        breakdown.append(
            {
                "window_id": window.window_id,
                "symbol": window.symbol,
                "start_date": window.start_date.isoformat(),
                "end_date": window.end_date.isoformat(),
                "capturable_return": round(window.capturable_return, 6),
                "capture_ratio": round(capture_ratio, 6),
                "missed": capture_ratio < min_effective_capture,
            }
        )
    return breakdown


def _window_capture_ratio(
    closed_trades: list[ClosedTrade],
    window: MainlineWindow,
) -> float:
    if window.capturable_return <= 0.0:
        return 0.0

    captured_return = 0.0
    for trade in closed_trades:
        if trade.symbol != window.symbol:
            continue
        if trade.exit_date < window.start_date or trade.entry_date > window.end_date:
            continue
        entry_notional = trade.entry_price * trade.quantity
        if entry_notional <= 0.0:
            continue
        trade_return = max(trade.pnl, 0.0) / entry_notional
        captured_return += trade_return

    return min(captured_return / window.capturable_return, 1.0)


def build_summary(initial_cash: float, result: BacktestResult) -> dict[str, float | int | str]:
    payoff = payoff_ratio(result.closed_trades)
    return {
        "total_return": round(total_return(initial_cash, result.equity_curve), 6),
        "max_drawdown": round(max_drawdown(result.equity_curve), 6),
        "win_rate": round(win_rate(result.closed_trades), 6),
        "payoff_ratio": round(payoff, 6) if isinstance(payoff, float) else payoff,
        "fill_count": len(result.fills),
        "closed_trade_count": len(result.closed_trades),
        "rejected_signal_count": len(result.rejected_signals),
    }
