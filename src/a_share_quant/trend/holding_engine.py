from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import AttackPermission, DailyBar, HierarchyAssignment, HoldingDecision


@dataclass(frozen=True, slots=True)
class HoldingConfig:
    medium_window: int = 3
    min_health_score_to_hold: float = 1.5


class HoldingEngine:
    """Assess whether an existing position still deserves to be held."""

    def __init__(self, config: HoldingConfig | None = None) -> None:
        self.config = config or HoldingConfig()

    def evaluate(
        self,
        bars: list[DailyBar],
        assignment: HierarchyAssignment,
        permission: AttackPermission,
    ) -> HoldingDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        health_score = 0.0
        reasons: list[str] = []

        if permission.is_attack_allowed and permission.approved_sector_id == assignment.sector_id:
            health_score += 1.0
            reasons.append("attack_permission_active")
        else:
            reasons.append("attack_permission_inactive")

        if assignment.layer in {"leader", "core", "late_mover"}:
            health_score += 1.0
            reasons.append("still_in_core_hierarchy")
        else:
            reasons.append("fell_out_of_core_hierarchy")

        if len(ordered) >= 3:
            ma_medium = self._moving_average(ordered, self.config.medium_window)
            if latest.close >= ma_medium:
                health_score += 1.0
                reasons.append("close_above_medium_trend")
            else:
                reasons.append("close_below_medium_trend")

            previous = ordered[-2]
            if latest.close >= previous.low:
                health_score += 0.5
                reasons.append("healthy_pullback_or_strength")
            else:
                reasons.append("pullback_too_deep")

        should_hold = health_score >= self.config.min_health_score_to_hold
        return HoldingDecision(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            should_hold=should_hold,
            reason=";".join(reasons),
            health_score=round(health_score, 6),
        )

    def _moving_average(self, bars: list[DailyBar], window: int) -> float:
        subset = bars[-window:]
        return sum(bar.close for bar in subset) / len(subset)
