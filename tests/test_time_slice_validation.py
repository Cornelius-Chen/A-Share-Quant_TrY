from __future__ import annotations

from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.rule_sweep import RuleCandidate
from a_share_quant.strategy.time_slice_validation import TimeSliceValidationRunner, ValidationSlice


def build_bar(symbol: str, trade_date: date) -> DailyBar:
    return DailyBar(
        trade_date=trade_date,
        symbol=symbol,
        open=10.0,
        high=10.2,
        low=9.8,
        close=10.0,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=9.9,
        adjust_factor=1.0,
        listed_days=300,
    )


def build_sector_snapshot(trade_date: date) -> SectorSnapshot:
    return SectorSnapshot(
        trade_date=trade_date,
        sector_id="AI",
        sector_name="AI",
        persistence=0.8,
        diffusion=0.8,
        money_making=0.8,
        leader_strength=0.8,
        relative_strength=0.8,
        activity=0.8,
    )


def build_stock_snapshot(symbol: str, trade_date: date) -> StockSnapshot:
    return StockSnapshot(
        trade_date=trade_date,
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


def test_time_slice_validation_runner_expands_datasets_by_slice_and_candidate() -> None:
    engine = BacktestEngine(
        initial_cash=100000.0,
        cost_model=CostModel(commission_bps=0.0, stamp_tax_bps=0.0, min_commission=0.0),
        limit_model=LimitModel(daily_limit_pct=0.10, epsilon=0.0001),
    )
    runner = TimeSliceValidationRunner(engine=engine)
    config = {
        "regime": {"segmentation_method": "sector_trend"},
        "trend": {},
        "strategy": {"buy_quantity": 100},
    }
    dataset_pack = DatasetPack(
        dataset_name="baseline",
        config=config,
        bars=[
            build_bar("AAA", date(2025, 1, 2)),
            build_bar("AAA", date(2025, 2, 3)),
        ],
        index_bars=[],
        sector_snapshots=[
            build_sector_snapshot(date(2025, 1, 2)),
            build_sector_snapshot(date(2025, 2, 3)),
        ],
        stock_snapshots=[
            build_stock_snapshot("AAA", date(2025, 1, 2)),
            build_stock_snapshot("AAA", date(2025, 2, 3)),
        ],
        mainline_windows=[
            MainlineWindow(
                window_id="aaa_1",
                symbol="AAA",
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 2),
                capturable_return=0.0,
            ),
            MainlineWindow(
                window_id="aaa_2",
                symbol="AAA",
                start_date=date(2025, 2, 3),
                end_date=date(2025, 2, 3),
                capturable_return=0.0,
            ),
        ],
    )
    result = runner.run(
        strategy_names=["mainline_trend_a"],
        dataset_packs=[dataset_pack],
        candidates=[
            RuleCandidate(candidate_name="control", description=None, override={}),
            RuleCandidate(candidate_name="strict", description=None, override={"regime": {"min_top_score": 3.0}}),
        ],
        slices=[
            ValidationSlice("slice_1", date(2025, 1, 1), date(2025, 1, 31)),
            ValidationSlice("slice_2", date(2025, 2, 1), date(2025, 2, 28)),
        ],
    )

    rows = result.comparison_rows()
    leaderboard = result.candidate_leaderboard()
    summary = result.aggregate_summary()
    slice_summary = result.slice_summary()

    assert len(rows) == 4
    assert {row["slice_name"] for row in rows} == {"slice_1", "slice_2"}
    assert {row["candidate_name"] for row in rows} == {"control", "strict"}
    assert len(leaderboard) == 2
    assert summary["slice_count"] == 2
    assert len(slice_summary) == 2
