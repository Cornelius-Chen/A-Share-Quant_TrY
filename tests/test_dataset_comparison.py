from __future__ import annotations

from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.dataset_comparison import DatasetComparisonRunner, DatasetPack


def build_bar(symbol: str) -> DailyBar:
    return DailyBar(
        trade_date=date(2025, 1, 2),
        symbol=symbol,
        open=10.0,
        high=10.1,
        low=9.9,
        close=10.0,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=9.9,
        adjust_factor=1.0,
        listed_days=300,
    )


def build_sector_snapshot() -> SectorSnapshot:
    return SectorSnapshot(
        trade_date=date(2025, 1, 2),
        sector_id="AI",
        sector_name="AI",
        persistence=0.8,
        diffusion=0.8,
        money_making=0.8,
        leader_strength=0.8,
        relative_strength=0.8,
        activity=0.8,
    )


def build_stock_snapshot(symbol: str) -> StockSnapshot:
    return StockSnapshot(
        trade_date=date(2025, 1, 2),
        symbol=symbol,
        sector_id="AI",
        sector_name="AI",
        expected_upside=0.8,
        drive_strength=0.8,
        stability=0.8,
        liquidity=0.8,
        late_mover_quality=0.8,
        resonance=0.8,
    )


def test_dataset_comparison_runner_emits_rows_for_each_dataset_and_strategy() -> None:
    engine = BacktestEngine(
        initial_cash=100000.0,
        cost_model=CostModel(commission_bps=0.0, stamp_tax_bps=0.0, min_commission=0.0),
        limit_model=LimitModel(daily_limit_pct=0.10, epsilon=0.0001),
    )
    runner = DatasetComparisonRunner(engine=engine)
    config = {
        "regime": {"segmentation_method": "sector_trend"},
        "trend": {},
        "strategy": {"buy_quantity": 100},
    }
    dataset_packs = [
        DatasetPack(
            dataset_name="baseline",
            config=config,
            bars=[build_bar("AAA")],
            index_bars=[],
            sector_snapshots=[build_sector_snapshot()],
            stock_snapshots=[build_stock_snapshot("AAA")],
            mainline_windows=[
                MainlineWindow(
                    window_id="aaa_1",
                    symbol="AAA",
                    start_date=date(2025, 1, 2),
                    end_date=date(2025, 1, 2),
                    capturable_return=0.0,
                )
            ],
        ),
        DatasetPack(
            dataset_name="theme",
            config=config,
            bars=[build_bar("BBB")],
            index_bars=[],
            sector_snapshots=[build_sector_snapshot()],
            stock_snapshots=[build_stock_snapshot("BBB")],
            mainline_windows=[
                MainlineWindow(
                    window_id="bbb_1",
                    symbol="BBB",
                    start_date=date(2025, 1, 2),
                    end_date=date(2025, 1, 2),
                    capturable_return=0.0,
                )
            ],
        ),
    ]

    result = runner.run(
        strategy_names=["mainline_trend_a", "mainline_trend_b"],
        dataset_packs=dataset_packs,
    )
    rows = result.comparison_rows()

    assert len(rows) == 4
    assert {row["dataset_name"] for row in rows} == {"baseline", "theme"}
    assert {row["strategy_name"] for row in rows} == {"mainline_trend_a", "mainline_trend_b"}
