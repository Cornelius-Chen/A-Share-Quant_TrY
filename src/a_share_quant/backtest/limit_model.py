from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import DailyBar


@dataclass(frozen=True, slots=True)
class LimitModel:
    daily_limit_pct: float = 0.10
    epsilon: float = 0.0001

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "LimitModel":
        return cls(
            daily_limit_pct=float(config.get("daily_limit_pct", 0.10)),
            epsilon=float(config.get("epsilon", 0.0001)),
        )

    def _limit_up_price(self, bar: DailyBar) -> float:
        return bar.pre_close * (1.0 + self.daily_limit_pct)

    def _limit_down_price(self, bar: DailyBar) -> float:
        return bar.pre_close * (1.0 - self.daily_limit_pct)

    def can_fill(self, action: str, bar: DailyBar, price: float) -> bool:
        """Reject fills when suspension or limit conditions make them unreliable."""
        if bar.is_suspended:
            return False
        if action.lower() == "buy":
            return price < self._limit_up_price(bar) - self.epsilon
        if action.lower() == "sell":
            return price > self._limit_down_price(bar) + self.epsilon
        raise ValueError(f"Unsupported action: {action}")
