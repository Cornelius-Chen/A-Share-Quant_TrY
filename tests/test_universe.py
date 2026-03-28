from __future__ import annotations

from datetime import date

from a_share_quant.common.models import DailyBar
from a_share_quant.data.universe import UniverseFilter


def test_universe_filter_enforces_basic_constraints() -> None:
    bars = [
        DailyBar(
            trade_date=date(2025, 1, 2),
            symbol="AAA",
            open=10.0,
            high=10.2,
            low=9.8,
            close=10.1,
            volume=1000,
            turnover=60_000_000,
            pre_close=10.0,
            adjust_factor=1.0,
            is_st=False,
            is_suspended=False,
            listed_days=120,
        ),
        DailyBar(
            trade_date=date(2025, 1, 2),
            symbol="BBB",
            open=2.0,
            high=2.1,
            low=1.9,
            close=2.0,
            volume=1000,
            turnover=20_000_000,
            pre_close=2.0,
            adjust_factor=1.0,
            is_st=True,
            is_suspended=False,
            listed_days=20,
        ),
    ]

    filtered = UniverseFilter().apply(bars)

    assert [bar.symbol for bar in filtered] == ["AAA"]
