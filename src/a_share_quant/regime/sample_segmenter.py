from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.common.models import DailyBar, MainlineSectorScore, SampleSegment


@dataclass(frozen=True, slots=True)
class SegmenterConfig:
    min_segment_length: int = 2
    index_window: int = 2
    index_min_return: float = 0.01
    sector_score_threshold: float = 4.0


class SampleSegmenter:
    """Build reproducible bullish-window segments for index, sector, or resonance methods."""

    def __init__(self, config: SegmenterConfig | None = None) -> None:
        self.config = config or SegmenterConfig()

    def segment_by_index_trend(self, index_bars: list[DailyBar]) -> list[SampleSegment]:
        signals: list[tuple[date, bool]] = []
        sorted_bars = sorted(index_bars, key=lambda bar: bar.trade_date)
        for index, bar in enumerate(sorted_bars):
            if index < self.config.index_window:
                signals.append((bar.trade_date, False))
                continue
            baseline = sorted_bars[index - self.config.index_window].close
            rolling_return = bar.close / baseline - 1.0
            signals.append((bar.trade_date, rolling_return >= self.config.index_min_return))
        return self._build_segments(
            signals=signals,
            method="index_trend",
            trigger=f"rolling_return>={self.config.index_min_return:.4f}",
        )

    def segment_by_sector_trend(
        self,
        sector_scores: list[MainlineSectorScore],
    ) -> list[SampleSegment]:
        top_by_date: dict[date, MainlineSectorScore] = {}
        for score in sorted(sector_scores, key=lambda item: (item.trade_date, item.rank)):
            top_by_date.setdefault(score.trade_date, score)
        signals = [
            (
                trade_date,
                score.composite_score >= self.config.sector_score_threshold,
            )
            for trade_date, score in sorted(top_by_date.items())
        ]
        return self._build_segments(
            signals=signals,
            method="sector_trend",
            trigger=f"top_sector_score>={self.config.sector_score_threshold:.4f}",
        )

    def segment_by_resonance(
        self,
        index_bars: list[DailyBar],
        sector_scores: list[MainlineSectorScore],
    ) -> list[SampleSegment]:
        index_flags = {
            segment_day: is_active
            for segment_day, is_active in self._index_signals(index_bars)
        }
        sector_flags = {
            segment_day: is_active
            for segment_day, is_active in self._sector_signals(sector_scores)
        }
        trade_dates = sorted(set(index_flags) & set(sector_flags))
        signals = [
            (trade_date, index_flags[trade_date] and sector_flags[trade_date])
            for trade_date in trade_dates
        ]
        return self._build_segments(
            signals=signals,
            method="resonance",
            trigger="index_trend_and_sector_trend",
        )

    def _index_signals(self, index_bars: list[DailyBar]) -> list[tuple[date, bool]]:
        sorted_bars = sorted(index_bars, key=lambda bar: bar.trade_date)
        signals: list[tuple[date, bool]] = []
        for index, bar in enumerate(sorted_bars):
            if index < self.config.index_window:
                signals.append((bar.trade_date, False))
                continue
            baseline = sorted_bars[index - self.config.index_window].close
            rolling_return = bar.close / baseline - 1.0
            signals.append((bar.trade_date, rolling_return >= self.config.index_min_return))
        return signals

    def _sector_signals(
        self,
        sector_scores: list[MainlineSectorScore],
    ) -> list[tuple[date, bool]]:
        top_by_date: dict[date, MainlineSectorScore] = {}
        for score in sorted(sector_scores, key=lambda item: (item.trade_date, item.rank)):
            top_by_date.setdefault(score.trade_date, score)
        return [
            (
                trade_date,
                score.composite_score >= self.config.sector_score_threshold,
            )
            for trade_date, score in sorted(top_by_date.items())
        ]

    def _build_segments(
        self,
        *,
        signals: list[tuple[date, bool]],
        method: str,
        trigger: str,
    ) -> list[SampleSegment]:
        segments: list[SampleSegment] = []
        active_start: date | None = None
        active_dates: list[date] = []

        for trade_date, is_active in signals:
            if is_active:
                active_start = active_start or trade_date
                active_dates.append(trade_date)
                continue

            if active_start is not None and len(active_dates) >= self.config.min_segment_length:
                segments.append(
                    self._make_segment(
                        method=method,
                        start_date=active_start,
                        end_date=active_dates[-1],
                        length=len(active_dates),
                        trigger=trigger,
                    )
                )
            active_start = None
            active_dates = []

        if active_start is not None and len(active_dates) >= self.config.min_segment_length:
            segments.append(
                self._make_segment(
                    method=method,
                    start_date=active_start,
                    end_date=active_dates[-1],
                    length=len(active_dates),
                    trigger=trigger,
                )
            )
        return segments

    def _make_segment(
        self,
        *,
        method: str,
        start_date: date,
        end_date: date,
        length: int,
        trigger: str,
    ) -> SampleSegment:
        return SampleSegment(
            segment_id=f"{method}:{start_date.isoformat()}:{end_date.isoformat()}",
            method=method,
            start_date=start_date,
            end_date=end_date,
            length=length,
            trigger=trigger,
        )
