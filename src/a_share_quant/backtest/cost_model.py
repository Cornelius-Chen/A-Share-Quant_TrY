from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostModel:
    commission_bps: float = 3.0
    stamp_tax_bps: float = 10.0
    min_commission: float = 5.0

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "CostModel":
        return cls(
            commission_bps=float(config.get("commission_bps", 3.0)),
            stamp_tax_bps=float(config.get("stamp_tax_bps", 10.0)),
            min_commission=float(config.get("min_commission", 5.0)),
        )

    def calculate(self, notional: float, action: str) -> float:
        commission = max(notional * self.commission_bps / 10_000.0, self.min_commission)
        stamp_tax = 0.0
        if action.lower() == "sell":
            stamp_tax = notional * self.stamp_tax_bps / 10_000.0
        return commission + stamp_tax
