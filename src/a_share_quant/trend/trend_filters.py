from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import DailyBar, TrendFilterDecision


@dataclass(frozen=True, slots=True)
class TrendFilterConfig:
    short_window: int = 2
    medium_window: int = 3
    long_window: int = 4
    loose_window: int = 5
    repair_window: int = 3


class TrendFilters:
    """Evaluate protocol v1.0 trend-filter candidates on daily bars."""

    def __init__(self, config: TrendFilterConfig | None = None) -> None:
        self.config = config or TrendFilterConfig()

    def evaluate(self, bars: list[DailyBar]) -> list[TrendFilterDecision]:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        if not ordered:
            return []
        latest = ordered[-1]
        return [
            self.strict_short_term_bullish(ordered),
            self.medium_term_uptrend(ordered),
            self.loose_uptrend(ordered),
            self.pullback_repair(ordered),
        ]

    def strict_short_term_bullish(self, bars: list[DailyBar]) -> TrendFilterDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return TrendFilterDecision(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                filter_name="strict_short_term_bullish",
                passed=False,
                reason="insufficient_history",
            )
        ma_short = self._moving_average(ordered, self.config.short_window)
        ma_medium = self._moving_average(ordered, self.config.medium_window)
        ma_long = self._moving_average(ordered, self.config.long_window)
        passed = ma_short > ma_medium > ma_long and latest.close > ma_short
        reason = "short>medium>long_and_close_above_short" if passed else "alignment_not_strict_enough"
        return TrendFilterDecision(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            filter_name="strict_short_term_bullish",
            passed=passed,
            reason=reason,
        )

    def medium_term_uptrend(self, bars: list[DailyBar]) -> TrendFilterDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return TrendFilterDecision(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                filter_name="medium_term_uptrend",
                passed=False,
                reason="insufficient_history",
            )
        ma_medium = self._moving_average(ordered, self.config.medium_window)
        ma_long = self._moving_average(ordered, self.config.long_window)
        passed = latest.close > ma_medium and ma_medium >= ma_long
        reason = "close_above_medium_and_medium>=long" if passed else "medium_trend_not_up"
        return TrendFilterDecision(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            filter_name="medium_term_uptrend",
            passed=passed,
            reason=reason,
        )

    def loose_uptrend(self, bars: list[DailyBar]) -> TrendFilterDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        lookback = ordered[-self.config.loose_window :]
        passed = latest.close > lookback[0].close and latest.close >= min(bar.close for bar in lookback)
        reason = "latest_close_above_window_start" if passed else "loose_trend_not_up"
        return TrendFilterDecision(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            filter_name="loose_uptrend",
            passed=passed,
            reason=reason,
        )

    def pullback_repair(self, bars: list[DailyBar]) -> TrendFilterDecision:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return TrendFilterDecision(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                filter_name="pullback_repair",
                passed=False,
                reason="insufficient_history",
            )
        repair_bars = ordered[-self.config.repair_window :]
        prior = repair_bars[-2] if len(repair_bars) >= 2 else repair_bars[-1]
        reference = repair_bars[0]
        passed = (
            len(repair_bars) >= 3
            and prior.close <= reference.close
            and latest.close > prior.high
            and latest.close > reference.close
        )
        reason = "pullback_then_restrengthening" if passed else "repair_pattern_not_present"
        return TrendFilterDecision(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            filter_name="pullback_repair",
            passed=passed,
            reason=reason,
        )

    def _moving_average(self, bars: list[DailyBar], window: int) -> float:
        subset = bars[-window:]
        return sum(bar.close for bar in subset) / len(subset)
