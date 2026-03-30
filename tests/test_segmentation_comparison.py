from __future__ import annotations

from datetime import date

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.models import DailyBar, MainlineWindow, SectorSnapshot, StockSnapshot
from a_share_quant.strategy.segmentation_comparison import SegmentationComparisonRunner


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


def test_segmentation_comparison_runner_compares_methods() -> None:
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
    windows = [
        MainlineWindow("w1", "LDR", date(2025, 1, 8), date(2025, 1, 10), 0.08),
        MainlineWindow("w2", "CORE", date(2025, 1, 8), date(2025, 1, 10), 0.04),
        MainlineWindow("w3", "LATE", date(2025, 1, 8), date(2025, 1, 10), 0.06),
    ]
    config = {
        "regime": {
            "segmentation_method": "sector_trend",
            "index_window": 2,
            "index_min_return": 0.01,
            "sector_score_threshold": 4.0,
            "min_segment_length": 2,
            "min_top_score": 4.0,
            "min_score_margin": 0.2,
        },
        "trend": {
            "hierarchy": {
                "min_resonance_for_core": 0.55,
                "min_quality_for_late_mover": 0.55,
                "min_composite_for_non_junk": 0.60,
            },
            "filters": {},
            "entry_rules": {},
            "holding": {},
            "exit_guard": {},
        },
        "strategy": {"buy_quantity": 100},
    }
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
    runner = SegmentationComparisonRunner(engine=engine, config=config)
    comparison = runner.run(
        strategy_name="mainline_trend_c",
        segmentation_methods=["index_trend", "sector_trend", "resonance"],
        bars=bars,
        index_bars=index_bars,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=windows,
    )

    rows = comparison.comparison_rows()
    assert [row["segmentation_method"] for row in rows] == [
        "index_trend",
        "sector_trend",
        "resonance",
    ]
    assert rows[0]["ranks"]["total_return"] >= 1
    assert comparison.aggregate_summary()["comparison_count"] == 3
