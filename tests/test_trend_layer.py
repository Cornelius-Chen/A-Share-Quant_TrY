from __future__ import annotations

from datetime import date

from a_share_quant.common.models import DailyBar, StockSnapshot
from a_share_quant.trend.entry_rules import EntryRules
from a_share_quant.trend.leader_hierarchy_ranker import HierarchyConfig, LeaderHierarchyRanker
from a_share_quant.trend.trend_filters import TrendFilters


def build_bar(
    trade_date: str,
    close_price: float,
    *,
    open_price: float | None = None,
    high_price: float | None = None,
    low_price: float | None = None,
    symbol: str = "AAA",
) -> DailyBar:
    open_value = close_price if open_price is None else open_price
    high_value = max(open_value, close_price) if high_price is None else high_price
    low_value = min(open_value, close_price) if low_price is None else low_price
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        open=open_value,
        high=high_value,
        low=low_value,
        close=close_price,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=open_value,
        adjust_factor=1.0,
        listed_days=200,
    )


def test_leader_hierarchy_ranker_assigns_four_protocol_layers() -> None:
    snapshots = [
        StockSnapshot(date(2025, 1, 7), "LDR", "AI", "AI", 0.95, 0.95, 0.55, 0.60, 0.30, 0.90),
        StockSnapshot(date(2025, 1, 7), "CORE", "AI", "AI", 0.60, 0.55, 0.95, 0.95, 0.40, 0.85),
        StockSnapshot(date(2025, 1, 7), "LATE", "AI", "AI", 0.72, 0.50, 0.60, 0.55, 0.92, 0.75),
        StockSnapshot(date(2025, 1, 7), "JUNK", "AI", "AI", 0.35, 0.20, 0.30, 0.25, 0.30, 0.20),
    ]

    assignments = LeaderHierarchyRanker().rank(snapshots)
    layers = {item.symbol: item.layer for item in assignments}

    assert layers["LDR"] == "leader"
    assert layers["CORE"] == "core"
    assert layers["LATE"] == "late_mover"
    assert layers["JUNK"] == "junk"


def test_trend_filters_compare_multiple_candidates() -> None:
    bars = [
        build_bar("2025-01-02", 10.0),
        build_bar("2025-01-03", 10.3, high_price=10.35),
        build_bar("2025-01-06", 10.6, high_price=10.65),
        build_bar("2025-01-07", 10.4, high_price=10.45),
        build_bar("2025-01-08", 10.8, high_price=10.85),
    ]

    decisions = {item.filter_name: item for item in TrendFilters().evaluate(bars)}

    assert decisions["medium_term_uptrend"].passed is True
    assert decisions["loose_uptrend"].passed is True
    assert decisions["pullback_repair"].passed is True


def test_entry_rules_emit_multiple_candidate_entries() -> None:
    bars = [
        build_bar("2025-01-02", 10.0, high_price=10.10, low_price=9.90),
        build_bar("2025-01-03", 10.2, high_price=10.25, low_price=10.00),
        build_bar("2025-01-06", 10.5, high_price=10.55, low_price=10.20),
        build_bar("2025-01-07", 10.3, high_price=10.35, low_price=10.05),
        build_bar("2025-01-08", 10.7, high_price=10.75, low_price=10.25),
    ]

    entries = {item.rule_name: item for item in EntryRules().evaluate(bars)}

    assert entries["confirmation_entry"].triggered is True
    assert entries["mid_trend_follow"].triggered is False
    assert entries["pullback_then_restrengthening"].triggered is True
    assert entries["second_breakout"].triggered is True


def test_leader_hierarchy_ranker_can_condition_late_quality_on_theme_turnover_context() -> None:
    snapshots = [
        StockSnapshot(
            date(2025, 1, 7),
            "LDR",
            "AI",
            "AI",
            0.95,
            0.95,
            0.55,
            0.60,
            0.30,
            0.90,
        ),
        StockSnapshot(
            date(2025, 1, 7),
            "CORE",
            "AI",
            "AI",
            0.60,
            0.55,
            0.95,
            0.95,
            0.40,
            0.85,
        ),
        StockSnapshot(
            date(2025, 1, 7),
            "CTX",
            "AI",
            "AI",
            0.72,
            0.50,
            0.60,
            0.55,
            0.53,
            0.75,
            non_junk_composite_score=0.72,
            context_theme_turnover_interaction=0.29,
        ),
        StockSnapshot(
            date(2025, 1, 7),
            "JUNK",
            "AI",
            "AI",
            0.35,
            0.20,
            0.30,
            0.25,
            0.30,
            0.20,
        ),
    ]

    default_layers = {
        item.symbol: item.layer
        for item in LeaderHierarchyRanker().rank(snapshots)
    }
    conditioned_layers = {
        item.symbol: item.layer
        for item in LeaderHierarchyRanker(
            HierarchyConfig(
                min_resonance_for_core=0.55,
                min_quality_for_late_mover=0.55,
                min_composite_for_non_junk=0.55,
                enable_context_conditioned_late_quality=True,
                conditioned_high_interaction_threshold=0.25,
                conditioned_medium_interaction_threshold=0.18,
                conditioned_high_interaction_relief=0.03,
                conditioned_medium_interaction_relief=0.02,
                conditioned_resonance_floor=0.40,
            )
        ).rank(snapshots)
    }

    assert default_layers["CTX"] == "junk"
    assert conditioned_layers["CTX"] == "late_mover"
