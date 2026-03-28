from __future__ import annotations

from dataclasses import dataclass

from a_share_quant.common.models import DailyBar, EntryCandidate


@dataclass(frozen=True, slots=True)
class EntryRuleConfig:
    confirmation_window: int = 2
    medium_window: int = 3
    breakout_lookback: int = 4


class EntryRules:
    """Evaluate protocol v1.0 entry-rule candidates on daily bars."""

    def __init__(self, config: EntryRuleConfig | None = None) -> None:
        self.config = config or EntryRuleConfig()

    def evaluate(self, bars: list[DailyBar]) -> list[EntryCandidate]:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        if not ordered:
            return []
        return [
            self.confirmation_entry(ordered),
            self.mid_trend_follow(ordered),
            self.pullback_then_restrengthening(ordered),
            self.second_breakout(ordered),
        ]

    def confirmation_entry(self, bars: list[DailyBar]) -> EntryCandidate:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return EntryCandidate(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                rule_name="confirmation_entry",
                triggered=False,
                reason="insufficient_history",
            )
        previous = ordered[-2]
        triggered = latest.close > previous.high and latest.close > previous.close
        reason = "close_breaks_previous_high" if triggered else "confirmation_not_met"
        return EntryCandidate(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            rule_name="confirmation_entry",
            triggered=triggered,
            reason=reason,
        )

    def mid_trend_follow(self, bars: list[DailyBar]) -> EntryCandidate:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return EntryCandidate(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                rule_name="mid_trend_follow",
                triggered=False,
                reason="insufficient_history",
            )
        ma_medium = self._moving_average(ordered, self.config.medium_window)
        recent_closes = [bar.close for bar in ordered[-3:]]
        triggered = latest.close > ma_medium and recent_closes == sorted(recent_closes)
        reason = "close_above_medium_with_rising_closes" if triggered else "mid_trend_follow_not_met"
        return EntryCandidate(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            rule_name="mid_trend_follow",
            triggered=triggered,
            reason=reason,
        )

    def pullback_then_restrengthening(self, bars: list[DailyBar]) -> EntryCandidate:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 3:
            return EntryCandidate(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                rule_name="pullback_then_restrengthening",
                triggered=False,
                reason="insufficient_history",
            )
        previous = ordered[-2]
        earlier = ordered[-3]
        ma_medium = self._moving_average(ordered, self.config.medium_window)
        triggered = (
            previous.close < earlier.close
            and latest.close > previous.high
            and latest.close > ma_medium
        )
        reason = "pullback_then_strength_recovery" if triggered else "restrengthening_not_met"
        return EntryCandidate(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            rule_name="pullback_then_restrengthening",
            triggered=triggered,
            reason=reason,
        )

    def second_breakout(self, bars: list[DailyBar]) -> EntryCandidate:
        ordered = sorted(bars, key=lambda bar: bar.trade_date)
        latest = ordered[-1]
        if len(ordered) < 4:
            return EntryCandidate(
                trade_date=latest.trade_date,
                symbol=latest.symbol,
                rule_name="second_breakout",
                triggered=False,
                reason="insufficient_history",
            )
        lookback = ordered[-self.config.breakout_lookback :]
        prior_peak = max(bar.high for bar in lookback[:-1])
        consolidation_low = min(bar.low for bar in lookback[-3:-1])
        triggered = latest.close > prior_peak and consolidation_low < prior_peak
        reason = "breaks_prior_peak_after_consolidation" if triggered else "second_breakout_not_met"
        return EntryCandidate(
            trade_date=latest.trade_date,
            symbol=latest.symbol,
            rule_name="second_breakout",
            triggered=triggered,
            reason=reason,
        )

    def _moving_average(self, bars: list[DailyBar], window: int) -> float:
        subset = bars[-window:]
        return sum(bar.close for bar in subset) / len(subset)
