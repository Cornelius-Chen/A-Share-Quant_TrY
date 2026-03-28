from __future__ import annotations

from datetime import date

from a_share_quant.backtest.metrics import mainline_capture_ratio, missed_mainline_count
from a_share_quant.common.models import ClosedTrade, MainlineWindow


def test_mainline_capture_ratio_aggregates_window_capture() -> None:
    trades = [
        ClosedTrade(
            symbol="AAA",
            entry_date=date(2025, 1, 3),
            exit_date=date(2025, 1, 7),
            quantity=100,
            entry_price=10.0,
            exit_price=11.0,
            fees=0.0,
            pnl=100.0,
            holding_days=4,
        )
    ]
    windows = [
        MainlineWindow(
            window_id="w1",
            symbol="AAA",
            start_date=date(2025, 1, 2),
            end_date=date(2025, 1, 8),
            capturable_return=0.20,
        )
    ]

    ratio = mainline_capture_ratio(trades, windows)

    assert ratio == 0.5


def test_missed_mainline_count_flags_low_capture_windows() -> None:
    trades = [
        ClosedTrade(
            symbol="AAA",
            entry_date=date(2025, 1, 3),
            exit_date=date(2025, 1, 7),
            quantity=100,
            entry_price=10.0,
            exit_price=10.3,
            fees=0.0,
            pnl=30.0,
            holding_days=4,
        )
    ]
    windows = [
        MainlineWindow(
            window_id="w1",
            symbol="AAA",
            start_date=date(2025, 1, 2),
            end_date=date(2025, 1, 8),
            capturable_return=0.20,
        ),
        MainlineWindow(
            window_id="w2",
            symbol="BBB",
            start_date=date(2025, 1, 2),
            end_date=date(2025, 1, 8),
            capturable_return=0.15,
        ),
    ]

    missed = missed_mainline_count(trades, windows, min_effective_capture=0.20)

    assert missed == 2
