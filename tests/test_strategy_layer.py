from __future__ import annotations

from datetime import date

from a_share_quant.common.models import AttackPermission, DailyBar, HierarchyAssignment
from a_share_quant.strategy.mainline_strategy_base import StrategyConfig
from a_share_quant.strategy.mainline_trend_a import MainlineTrendA
from a_share_quant.strategy.mainline_trend_b import MainlineTrendB
from a_share_quant.strategy.mainline_trend_c import MainlineTrendC
from a_share_quant.trend.exit_guard import ExitGuard, ExitGuardConfig
from a_share_quant.trend.holding_engine import HoldingEngine


def build_bar(
    trade_date: str,
    close_price: float,
    *,
    symbol: str,
    high_price: float | None = None,
    low_price: float | None = None,
) -> DailyBar:
    high_value = close_price if high_price is None else high_price
    low_value = close_price if low_price is None else low_price
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol=symbol,
        open=close_price,
        high=high_value,
        low=low_value,
        close=close_price,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=close_price,
        adjust_factor=1.0,
        listed_days=200,
    )


def build_assignment(symbol: str, layer: str, layer_score: float = 0.9) -> HierarchyAssignment:
    return HierarchyAssignment(
        trade_date=date(2025, 1, 8),
        symbol=symbol,
        sector_id="AI",
        sector_name="AI",
        layer=layer,
        layer_score=layer_score,
        leader_score=0.9,
        core_score=0.8,
        late_score=0.7,
        reason=layer,
    )


def bullish_bars(symbol: str) -> list[DailyBar]:
    return [
        build_bar("2025-01-02", 10.0, symbol=symbol, high_price=10.10, low_price=9.90),
        build_bar("2025-01-03", 10.2, symbol=symbol, high_price=10.25, low_price=10.00),
        build_bar("2025-01-06", 10.5, symbol=symbol, high_price=10.55, low_price=10.20),
        build_bar("2025-01-07", 10.3, symbol=symbol, high_price=10.35, low_price=10.05),
        build_bar("2025-01-08", 10.7, symbol=symbol, high_price=10.75, low_price=10.25),
    ]


def test_holding_and_exit_classify_hold_vs_mainline_decay() -> None:
    bars = bullish_bars("LDR")
    assignment = build_assignment("LDR", "leader")
    active_permission = AttackPermission(
        trade_date=date(2025, 1, 8),
        is_attack_allowed=True,
        approved_sector_id="AI",
        approved_sector_name="AI",
        score=5.0,
        reason="approved",
    )
    inactive_permission = AttackPermission(
        trade_date=date(2025, 1, 8),
        is_attack_allowed=False,
        approved_sector_id=None,
        approved_sector_name=None,
        score=None,
        reason="outside_segment",
    )

    holding = HoldingEngine().evaluate(bars, assignment, active_permission)
    exit_hold = ExitGuard().evaluate(bars, assignment, active_permission, holding)
    exit_decay = ExitGuard().evaluate(
        bars,
        assignment,
        inactive_permission,
        HoldingEngine().evaluate(bars, assignment, inactive_permission),
    )

    assert holding.should_hold is True
    assert exit_hold.should_exit is False
    assert exit_decay.should_exit is True
    assert exit_decay.category == "mainline_decay"


def test_strategy_families_buy_expected_layers() -> None:
    trade_date = date(2025, 1, 8)
    bars_by_symbol = {
        "LDR": bullish_bars("LDR"),
        "CORE": bullish_bars("CORE"),
        "LATE": bullish_bars("LATE"),
        "JUNK": bullish_bars("JUNK"),
    }
    permissions = [
        AttackPermission(
            trade_date=trade_date,
            is_attack_allowed=True,
            approved_sector_id="AI",
            approved_sector_name="AI",
            score=5.0,
            reason="approved",
        )
    ]
    assignments = [
        build_assignment("LDR", "leader", 0.95),
        build_assignment("CORE", "core", 0.90),
        build_assignment("LATE", "late_mover", 0.85),
        build_assignment("JUNK", "junk", 0.20),
    ]

    signals_a = MainlineTrendA().generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=assignments,
        current_positions={},
    )
    signals_b = MainlineTrendB().generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=assignments,
        current_positions={},
    )
    signals_c = MainlineTrendC().generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=assignments,
        current_positions={},
    )

    assert [signal.symbol for signal in signals_a] == ["LDR"]
    assert [signal.symbol for signal in signals_b] == ["LDR", "CORE"]
    assert [signal.symbol for signal in signals_c] == ["LDR", "CORE", "LATE"]


def test_strategy_sells_existing_position_when_sector_loses_permission() -> None:
    trade_date = date(2025, 1, 8)
    bars_by_symbol = {"LDR": bullish_bars("LDR")}
    permissions = [
        AttackPermission(
            trade_date=trade_date,
            is_attack_allowed=False,
            approved_sector_id=None,
            approved_sector_name=None,
            score=None,
            reason="outside_segment",
        )
    ]
    assignments = [build_assignment("LDR", "leader", 0.95)]

    signals = MainlineTrendA().generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=assignments,
        current_positions={"LDR": 200},
    )

    assert len(signals) == 1
    assert signals[0].action == "sell"
    assert signals[0].symbol == "LDR"
    assert signals[0].quantity == 200


def test_exit_guard_can_grace_single_junk_day_when_health_is_high() -> None:
    bars = bullish_bars("CORE")
    assignment = build_assignment("CORE", "junk")
    permission = AttackPermission(
        trade_date=date(2025, 1, 8),
        is_attack_allowed=True,
        approved_sector_id="AI",
        approved_sector_name="AI",
        score=5.0,
        reason="approved",
    )
    holding = HoldingEngine().evaluate(bars, assignment, permission)

    decision = ExitGuard(
        ExitGuardConfig(medium_window=3, junk_grace_min_health_score=1.5)
    ).evaluate(bars, assignment, permission, holding)

    assert decision.should_exit is False
    assert decision.category == "junk_grace_hold"


def test_mainline_trend_c_can_override_junk_for_high_score_late_mover_entry() -> None:
    trade_date = date(2025, 1, 8)
    bars_by_symbol = {"LATE": bullish_bars("LATE")}
    permissions = [
        AttackPermission(
            trade_date=trade_date,
            is_attack_allowed=True,
            approved_sector_id="AI",
            approved_sector_name="AI",
            score=5.0,
            reason="approved",
        )
    ]
    junk_late_candidate = HierarchyAssignment(
        trade_date=trade_date,
        symbol="LATE",
        sector_id="AI",
        sector_name="AI",
        layer="junk",
        layer_score=0.58,
        leader_score=0.55,
        core_score=0.57,
        late_score=0.66,
        reason="low_composite_or_low_resonance",
    )

    default_signals = MainlineTrendC().generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=[junk_late_candidate],
        current_positions={},
    )
    override_signals = MainlineTrendC(
        config=StrategyConfig(
            enable_late_mover_entry_override=True,
            late_mover_entry_override_min_layer_score=0.55,
            late_mover_entry_override_min_late_score=0.60,
        )
    ).generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=[junk_late_candidate],
        current_positions={},
    )
    strategy_b_signals = MainlineTrendB(
        config=StrategyConfig(
            enable_late_mover_entry_override=True,
            late_mover_entry_override_min_layer_score=0.55,
            late_mover_entry_override_min_late_score=0.60,
        )
    ).generate_signals(
        trade_date=trade_date,
        bars_by_symbol=bars_by_symbol,
        permissions=permissions,
        assignments=[junk_late_candidate],
        current_positions={},
    )

    assert default_signals == []
    assert [signal.symbol for signal in override_signals] == ["LATE"]
    assert strategy_b_signals == []
