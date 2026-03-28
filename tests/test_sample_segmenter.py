from __future__ import annotations

from datetime import date

from a_share_quant.common.models import DailyBar, MainlineSectorScore
from a_share_quant.regime.sample_segmenter import SampleSegmenter, SegmenterConfig


def build_bar(trade_date: str, close_price: float, pre_close: float) -> DailyBar:
    return DailyBar(
        trade_date=date.fromisoformat(trade_date),
        symbol="INDEX",
        open=close_price,
        high=close_price,
        low=close_price,
        close=close_price,
        volume=1_000_000,
        turnover=100_000_000,
        pre_close=pre_close,
        adjust_factor=1.0,
        listed_days=1000,
    )


def build_score(
    trade_date: str,
    sector_id: str,
    score: float,
    rank: int,
) -> MainlineSectorScore:
    return MainlineSectorScore(
        trade_date=date.fromisoformat(trade_date),
        sector_id=sector_id,
        sector_name=sector_id,
        composite_score=score,
        rank=rank,
        persistence=0.0,
        diffusion=0.0,
        money_making=0.0,
        leader_strength=0.0,
        relative_strength=0.0,
        activity=0.0,
    )


def test_segment_by_index_trend_builds_bullish_windows() -> None:
    bars = [
        build_bar("2025-01-02", 100.0, 100.0),
        build_bar("2025-01-03", 101.0, 100.0),
        build_bar("2025-01-06", 103.0, 101.0),
        build_bar("2025-01-07", 105.0, 103.0),
        build_bar("2025-01-08", 104.0, 105.0),
    ]
    segmenter = SampleSegmenter(
        SegmenterConfig(min_segment_length=2, index_window=2, index_min_return=0.02)
    )

    segments = segmenter.segment_by_index_trend(bars)

    assert len(segments) == 1
    assert segments[0].method == "index_trend"
    assert segments[0].start_date == date(2025, 1, 6)
    assert segments[0].end_date == date(2025, 1, 7)


def test_segment_by_resonance_requires_both_index_and_sector_signals() -> None:
    bars = [
        build_bar("2025-01-02", 100.0, 100.0),
        build_bar("2025-01-03", 101.0, 100.0),
        build_bar("2025-01-06", 103.0, 101.0),
        build_bar("2025-01-07", 105.0, 103.0),
    ]
    scores = [
        build_score("2025-01-02", "AI", 3.0, 1),
        build_score("2025-01-03", "AI", 4.1, 1),
        build_score("2025-01-06", "AI", 4.3, 1),
        build_score("2025-01-07", "AI", 4.2, 1),
    ]
    segmenter = SampleSegmenter(
        SegmenterConfig(
            min_segment_length=2,
            index_window=1,
            index_min_return=0.015,
            sector_score_threshold=4.0,
        )
    )

    segments = segmenter.segment_by_resonance(bars, scores)

    assert len(segments) == 1
    assert segments[0].method == "resonance"
    assert segments[0].start_date == date(2025, 1, 6)
    assert segments[0].end_date == date(2025, 1, 7)
