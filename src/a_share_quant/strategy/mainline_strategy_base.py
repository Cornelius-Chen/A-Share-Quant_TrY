from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.common.models import (
    AttackPermission,
    DailyBar,
    EntryCandidate,
    HierarchyAssignment,
    Signal,
    TrendFilterDecision,
)
from a_share_quant.trend.entry_rules import EntryRules
from a_share_quant.trend.exit_guard import ExitGuard
from a_share_quant.trend.holding_engine import HoldingEngine
from a_share_quant.trend.trend_filters import TrendFilters


@dataclass(frozen=True, slots=True)
class StrategyConfig:
    buy_quantity: int = 100
    enable_late_mover_entry_override: bool = False
    late_mover_entry_override_min_layer_score: float = 1.10
    late_mover_entry_override_min_late_score: float = 1.10
    late_mover_entry_override_allowed_reasons: tuple[str, ...] = (
        "fallback_to_junk",
        "low_composite_or_low_resonance",
    )


class BaseMainlineTrendStrategy:
    """Compose regime and trend primitives into daily buy/sell signals."""

    strategy_name = "base_mainline_trend"
    allowed_layers: tuple[str, ...] = ()

    def __init__(
        self,
        *,
        config: StrategyConfig | None = None,
        trend_filters: TrendFilters | None = None,
        entry_rules: EntryRules | None = None,
        holding_engine: HoldingEngine | None = None,
        exit_guard: ExitGuard | None = None,
    ) -> None:
        self.config = config or StrategyConfig()
        self.trend_filters = trend_filters or TrendFilters()
        self.entry_rules = entry_rules or EntryRules()
        self.holding_engine = holding_engine or HoldingEngine()
        self.exit_guard = exit_guard or ExitGuard()

    def generate_signals(
        self,
        *,
        trade_date: date,
        bars_by_symbol: dict[str, list[DailyBar]],
        permissions: list[AttackPermission],
        assignments: list[HierarchyAssignment],
        current_positions: dict[str, int],
        blocked_buy_symbols: set[str] | None = None,
        blocked_sell_symbols: set[str] | None = None,
    ) -> list[Signal]:
        blocked_buy_symbols = blocked_buy_symbols or set()
        blocked_sell_symbols = blocked_sell_symbols or set()
        permission = self._permission_for_date(permissions, trade_date)
        assignments_today = [
            assignment for assignment in assignments if assignment.trade_date == trade_date
        ]
        assignment_by_symbol = {assignment.symbol: assignment for assignment in assignments_today}

        signals: list[Signal] = []
        exiting_symbols: set[str] = set()

        for symbol, quantity in sorted(current_positions.items()):
            if symbol in blocked_sell_symbols:
                continue
            symbol_bars = self._bars_until_date(bars_by_symbol.get(symbol, []), trade_date)
            if not symbol_bars:
                continue
            assignment = assignment_by_symbol.get(symbol)
            if assignment is None:
                signals.append(
                    Signal(
                        trade_date=trade_date,
                        symbol=symbol,
                        action="sell",
                        quantity=quantity,
                    )
                )
                exiting_symbols.add(symbol)
                continue

            holding = self.holding_engine.evaluate(symbol_bars, assignment, permission)
            exit_decision = self.exit_guard.evaluate(symbol_bars, assignment, permission, holding)
            if exit_decision.should_exit:
                signals.append(
                    Signal(
                        trade_date=trade_date,
                        symbol=symbol,
                        action="sell",
                        quantity=quantity,
                    )
                )
                exiting_symbols.add(symbol)

        if not permission.is_attack_allowed:
            return signals

        for assignment in sorted(assignments_today, key=lambda item: item.layer_score, reverse=True):
            if not self._can_open_long_from_assignment(assignment):
                continue
            if assignment.sector_id != permission.approved_sector_id:
                continue
            if (
                assignment.symbol in current_positions
                or assignment.symbol in exiting_symbols
                or assignment.symbol in blocked_buy_symbols
            ):
                continue

            symbol_bars = self._bars_until_date(bars_by_symbol.get(assignment.symbol, []), trade_date)
            if not symbol_bars:
                continue
            filters = self.trend_filters.evaluate(symbol_bars)
            entries = self.entry_rules.evaluate(symbol_bars)
            if self._has_buy_confirmation(filters, entries):
                signals.append(
                    Signal(
                        trade_date=trade_date,
                        symbol=assignment.symbol,
                        action="buy",
                        quantity=self.config.buy_quantity,
                    )
                )
        return signals

    def _can_open_long_from_assignment(self, assignment: HierarchyAssignment) -> bool:
        if assignment.layer in self.allowed_layers:
            return True
        return self._is_late_mover_entry_override(assignment)

    def _is_late_mover_entry_override(self, assignment: HierarchyAssignment) -> bool:
        return (
            "late_mover" in self.allowed_layers
            and self.config.enable_late_mover_entry_override
            and assignment.layer == "junk"
            and assignment.reason in self.config.late_mover_entry_override_allowed_reasons
            and assignment.layer_score >= self.config.late_mover_entry_override_min_layer_score
            and assignment.late_score >= self.config.late_mover_entry_override_min_late_score
        )

    def _has_buy_confirmation(
        self,
        filters: list[TrendFilterDecision],
        entries: list[EntryCandidate],
    ) -> bool:
        return any(item.passed for item in filters) and any(item.triggered for item in entries)

    def _permission_for_date(
        self,
        permissions: list[AttackPermission],
        trade_date: date,
    ) -> AttackPermission:
        for permission in permissions:
            if permission.trade_date == trade_date:
                return permission
        return AttackPermission(
            trade_date=trade_date,
            is_attack_allowed=False,
            approved_sector_id=None,
            approved_sector_name=None,
            score=None,
            reason="missing_permission",
        )

    def _bars_until_date(self, bars: list[DailyBar], trade_date: date) -> list[DailyBar]:
        return [bar for bar in sorted(bars, key=lambda item: item.trade_date) if bar.trade_date <= trade_date]
