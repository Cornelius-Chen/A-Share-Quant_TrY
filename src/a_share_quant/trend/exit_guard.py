from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import (
    AttackPermission,
    DailyBar,
    ExitDecision,
    HierarchyAssignment,
    HoldingDecision,
)


@dataclass(frozen=True, slots=True)
class ExitGuardConfig:
    medium_window: int = 3


class ExitGuard:
    """Classify exit conditions using protocol v1.0 categories."""

    def __init__(self, config: ExitGuardConfig | None = None) -> None:
        self.config = config or ExitGuardConfig()

    def evaluate(
        self,
        bars: list[DailyBar],
        assignment: HierarchyAssignment,
        permission: AttackPermission,
        holding: HoldingDecision,
    ) -> ExitDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        previous = ordered[-2] if len(ordered) >= 2 else ordered[-1]
        ma_medium = self._moving_average(ordered, self.config.medium_window)

        if assignment.layer == "junk":
            return self._decision(latest, True, "stock_fell_out_of_core_hierarchy", "assignment_became_junk")

        if not permission.is_attack_allowed:
            return self._decision(latest, True, "mainline_decay", "attack_permission_removed")

        if permission.approved_sector_id is not None and permission.approved_sector_id != assignment.sector_id:
            return self._decision(latest, True, "replaced_by_new_mainline", "new_sector_approved")

        if assignment.layer == "leader" and latest.close < previous.low and latest.close < ma_medium:
            return self._decision(
                latest,
                True,
                "leader_negative_feedback_spillover",
                "leader_broke_previous_low_and_medium_trend",
            )

        if latest.close < previous.low and latest.close < ma_medium:
            return self._decision(latest, True, "structural_breakdown", "close_below_previous_low_and_medium_trend")

        if not holding.should_hold:
            return self._decision(latest, True, "structural_breakdown", "holding_health_below_threshold")

        if latest.close < previous.close:
            return self._decision(latest, False, "normal_pullback", "price_soft_but_structure_intact")

        return self._decision(latest, False, "hold", "structure_intact")

    def _decision(
        self,
        bar: DailyBar,
        should_exit: bool,
        category: str,
        reason: str,
    ) -> ExitDecision:
        return ExitDecision(
            trade_date=bar.trade_date,
            symbol=bar.symbol,
            should_exit=should_exit,
            category=category,
            reason=reason,
        )

    def _moving_average(self, bars: list[DailyBar], window: int) -> float:
        subset = bars[-window:]
        return sum(bar.close for bar in subset) / len(subset)
