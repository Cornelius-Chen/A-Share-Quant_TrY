from __future__ import annotations

from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner


def build_bar(trade_date: str, symbol: str, close_price: float, high: float, low: float) -> DailyBar:
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        open=close_price,
        high=high,
        low=low,
        close=close_price,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=close_price,
        adjust_factor=1.0,
        listed_days=200,
    )


def build_sector_snapshot(
    trade_date: str,
    sector_id: str,
    persistence: float,
    diffusion: float,
    money_making: float,
    leader_strength: float,
    relative_strength: float,
    activity: float,
) -> SectorSnapshot:
    return SectorSnapshot(
        trade_date=date.fromisoformat(trade_date),
        sector_id=sector_id,
        sector_name=sector_id,
        persistence=persistence,
        diffusion=diffusion,
        money_making=money_making,
        leader_strength=leader_strength,
        relative_strength=relative_strength,
        activity=activity,
    )


def build_stock_snapshot(
    trade_date: str,
    symbol: str,
    expected_upside: float,
    drive_strength: float,
    stability: float,
    liquidity: float,
    late_mover_quality: float,
    resonance: float,
) -> StockSnapshot:
    return StockSnapshot(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        sector_id="AI",
        sector_name="AI",
        expected_upside=expected_upside,
        drive_strength=drive_strength,
        stability=stability,
        liquidity=liquidity,
        late_mover_quality=late_mover_quality,
        resonance=resonance,
    )


def test_strategy_experiment_runner_produces_custom_metrics_and_signals() -> None:
    bars = []
    for symbol, base in [("LDR", 10.0), ("CORE", 20.0), ("LATE", 8.0)]:
        bars.extend(
            [
                build_bar("2025-01-02", symbol, base + 0.0, base + 0.10, base - 0.10),
                build_bar("2025-01-03", symbol, base + 0.2, base + 0.25, base + 0.0),
                build_bar("2025-01-06", symbol, base + 0.5, base + 0.55, base + 0.2),
                build_bar("2025-01-07", symbol, base + 0.3, base + 0.35, base + 0.05),
                build_bar("2025-01-08", symbol, base + 0.7, base + 0.75, base + 0.25),
                build_bar("2025-01-09", symbol, base + 0.4, base + 0.65, base + 0.2),
                build_bar("2025-01-10", symbol, base + 0.1, base + 0.40, base + 0.0),
            ]
        )

    sector_snapshots = [
        build_sector_snapshot("2025-01-06", "AI", 0.82, 0.80, 0.78, 0.86, 0.79, 0.80),
        build_sector_snapshot("2025-01-06", "CYCLE", 0.45, 0.40, 0.35, 0.42, 0.40, 0.38),
        build_sector_snapshot("2025-01-07", "AI", 0.84, 0.81, 0.79, 0.88, 0.80, 0.82),
        build_sector_snapshot("2025-01-07", "CYCLE", 0.46, 0.41, 0.36, 0.41, 0.39, 0.37),
        build_sector_snapshot("2025-01-08", "AI", 0.87, 0.84, 0.82, 0.91, 0.85, 0.86),
        build_sector_snapshot("2025-01-08", "CYCLE", 0.48, 0.43, 0.38, 0.42, 0.40, 0.39),
        build_sector_snapshot("2025-01-09", "AI", 0.45, 0.42, 0.40, 0.44, 0.43, 0.44),
        build_sector_snapshot("2025-01-09", "CYCLE", 0.43, 0.41, 0.39, 0.42, 0.41, 0.40),
    ]

    stock_snapshots = [
        build_stock_snapshot("2025-01-08", "LDR", 0.95, 0.96, 0.55, 0.62, 0.35, 0.92),
        build_stock_snapshot("2025-01-08", "CORE", 0.66, 0.60, 0.94, 0.95, 0.40, 0.88),
        build_stock_snapshot("2025-01-08", "LATE", 0.74, 0.56, 0.62, 0.58, 0.93, 0.78),
        build_stock_snapshot("2025-01-09", "LDR", 0.70, 0.68, 0.50, 0.58, 0.34, 0.62),
        build_stock_snapshot("2025-01-09", "CORE", 0.58, 0.52, 0.88, 0.91, 0.39, 0.76),
        build_stock_snapshot("2025-01-09", "LATE", 0.60, 0.48, 0.55, 0.54, 0.80, 0.66),
    ]

    windows = [
        MainlineWindow("w1", "LDR", date(2025, 1, 8), date(2025, 1, 10), 0.08),
        MainlineWindow("w2", "CORE", date(2025, 1, 8), date(2025, 1, 10), 0.04),
        MainlineWindow("w3", "LATE", date(2025, 1, 8), date(2025, 1, 10), 0.06),
    ]

    engine = BacktestEngine(
        initial_cash=1_000_000,
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
    runner = StrategyExperimentRunner(engine=engine)

    experiment = runner.run(
        strategy_name="mainline_trend_c",
        bars=bars,
        index_bars=None,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=windows,
    )

    assert experiment.backtest_result.summary["strategy_name"] == "mainline_trend_c"
    assert experiment.backtest_result.summary["signal_count"] == 6
    assert experiment.backtest_result.summary["mainline_capture_ratio"] >= 0.0
    assert experiment.backtest_result.summary["missed_mainline_count"] >= 0
    assert len(experiment.backtest_result.closed_trades) == 3
    assert len(experiment.window_breakdown) == 3
    assert experiment.segment_overview["segment_count"] >= 1
    assert "total_realized_pnl" in experiment.trade_overview


def test_strategy_experiment_runner_blocks_duplicate_buy_until_fill() -> None:
    bars = [
        build_bar("2025-01-06", "LDR", 10.2, 10.25, 10.00),
        build_bar("2025-01-07", "LDR", 10.5, 10.55, 10.20),
        build_bar("2025-01-08", "LDR", 10.7, 10.75, 10.25),
        build_bar("2025-01-10", "LDR", 10.9, 11.0, 10.6),
    ]
    sector_snapshots = [
        build_sector_snapshot("2025-01-08", "AI", 0.87, 0.84, 0.82, 0.91, 0.85, 0.86),
        build_sector_snapshot("2025-01-08", "CYCLE", 0.48, 0.43, 0.38, 0.42, 0.40, 0.39),
        build_sector_snapshot("2025-01-09", "AI", 0.86, 0.83, 0.81, 0.90, 0.84, 0.85),
        build_sector_snapshot("2025-01-09", "CYCLE", 0.47, 0.42, 0.37, 0.41, 0.39, 0.38),
    ]
    stock_snapshots = [
        build_stock_snapshot("2025-01-08", "LDR", 0.95, 0.96, 0.55, 0.62, 0.35, 0.92),
        build_stock_snapshot("2025-01-09", "LDR", 0.94, 0.95, 0.56, 0.63, 0.35, 0.91),
    ]

    engine = BacktestEngine(
        initial_cash=1_000_000,
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
    runner = StrategyExperimentRunner(engine=engine)

    experiment = runner.run(
        strategy_name="mainline_trend_a",
        bars=bars,
        index_bars=None,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=[],
    )

    assert experiment.backtest_result.summary["signal_count"] == 1


def test_strategy_experiment_runner_supports_resonance_segmentation() -> None:
    bars = []
    for symbol, base in [("LDR", 10.0), ("CORE", 20.0), ("LATE", 8.0)]:
        bars.extend(
            [
                build_bar("2025-01-02", symbol, base + 0.0, base + 0.10, base - 0.10),
                build_bar("2025-01-03", symbol, base + 0.2, base + 0.25, base + 0.0),
                build_bar("2025-01-06", symbol, base + 0.5, base + 0.55, base + 0.2),
                build_bar("2025-01-07", symbol, base + 0.3, base + 0.35, base + 0.05),
                build_bar("2025-01-08", symbol, base + 0.7, base + 0.75, base + 0.25),
                build_bar("2025-01-09", symbol, base + 0.4, base + 0.65, base + 0.2),
                build_bar("2025-01-10", symbol, base + 0.9, base + 1.00, base + 0.6),
            ]
        )
    index_bars = [
        build_bar("2025-01-02", "INDEX", 100.0, 100.2, 99.8),
        build_bar("2025-01-03", "INDEX", 101.0, 101.2, 100.8),
        build_bar("2025-01-06", "INDEX", 103.0, 103.2, 102.8),
        build_bar("2025-01-07", "INDEX", 104.0, 104.2, 103.8),
        build_bar("2025-01-08", "INDEX", 106.0, 106.2, 105.8),
        build_bar("2025-01-09", "INDEX", 105.0, 105.2, 104.8),
        build_bar("2025-01-10", "INDEX", 104.0, 104.1, 103.8),
    ]
    sector_snapshots = [
        build_sector_snapshot("2025-01-06", "AI", 0.82, 0.80, 0.78, 0.86, 0.79, 0.80),
        build_sector_snapshot("2025-01-06", "CYCLE", 0.45, 0.40, 0.35, 0.42, 0.40, 0.38),
        build_sector_snapshot("2025-01-07", "AI", 0.84, 0.81, 0.79, 0.88, 0.80, 0.82),
        build_sector_snapshot("2025-01-07", "CYCLE", 0.46, 0.41, 0.36, 0.41, 0.39, 0.37),
        build_sector_snapshot("2025-01-08", "AI", 0.87, 0.84, 0.82, 0.91, 0.85, 0.86),
        build_sector_snapshot("2025-01-08", "CYCLE", 0.48, 0.43, 0.38, 0.42, 0.40, 0.39),
        build_sector_snapshot("2025-01-09", "AI", 0.45, 0.42, 0.40, 0.44, 0.43, 0.44),
        build_sector_snapshot("2025-01-09", "CYCLE", 0.43, 0.41, 0.39, 0.42, 0.41, 0.40),
    ]
    stock_snapshots = [
        build_stock_snapshot("2025-01-08", "LDR", 0.95, 0.96, 0.55, 0.62, 0.35, 0.92),
        build_stock_snapshot("2025-01-08", "CORE", 0.66, 0.60, 0.94, 0.95, 0.40, 0.88),
        build_stock_snapshot("2025-01-08", "LATE", 0.74, 0.56, 0.62, 0.58, 0.93, 0.78),
        build_stock_snapshot("2025-01-09", "LDR", 0.70, 0.68, 0.50, 0.58, 0.34, 0.62),
        build_stock_snapshot("2025-01-09", "CORE", 0.58, 0.52, 0.88, 0.91, 0.39, 0.76),
        build_stock_snapshot("2025-01-09", "LATE", 0.60, 0.48, 0.55, 0.54, 0.80, 0.66),
    ]

    engine = BacktestEngine(
        initial_cash=1_000_000,
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
    runner = StrategyExperimentRunner(engine=engine, segmentation_method="resonance")

    experiment = runner.run(
        strategy_name="mainline_trend_c",
        bars=bars,
        index_bars=index_bars,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=[],
    )

    assert experiment.segment_overview["segmentation_method"] == "resonance"
    assert experiment.segment_overview["segment_count"] >= 1
