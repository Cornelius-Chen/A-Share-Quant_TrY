from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import DailyBar


@dataclass(frozen=True, slots=True)
class UniverseFilter:
    exclude_st: bool = True
    exclude_suspended: bool = True
    min_listed_days: int = 60
    min_turnover: float = 50_000_000.0
    min_close: float = 3.0

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "UniverseFilter":
        return cls(
            exclude_st=bool(config.get("exclude_st", True)),
            exclude_suspended=bool(config.get("exclude_suspended", True)),
            min_listed_days=int(config.get("min_listed_days", 60)),
            min_turnover=float(config.get("min_turnover", 50_000_000.0)),
            min_close=float(config.get("min_close", 3.0)),
        )

    def apply(self, bars: list[DailyBar]) -> list[DailyBar]:
        """Filter daily bars using conservative A-share universe constraints."""
        filtered: list[DailyBar] = []
        for bar in bars:
            if self.exclude_st and bar.is_st:
                continue
            if self.exclude_suspended and bar.is_suspended:
                continue
            if bar.listed_days < self.min_listed_days:
                continue
            if bar.turnover < self.min_turnover:
                continue
            if bar.close < self.min_close:
                continue
            filtered.append(bar)
        return filtered
