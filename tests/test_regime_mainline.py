from __future__ import annotations

from datetime import date

from a_share_quant.common.models import SectorSnapshot
from a_share_quant.regime.attack_permission_engine import (
    AttackPermissionConfig,
    AttackPermissionEngine,
)
from a_share_quant.regime.mainline_sector_scorer import MainlineSectorScorer
from a_share_quant.regime.sample_segmenter import SampleSegmenter, SegmenterConfig


def build_snapshot(
    trade_date: str,
    sector_id: str,
    sector_name: str,
    persistence: float,
    diffusion: float,
    money_making: float,
    leader_strength: float,
    relative_strength: float,
    activity: float,
) -> SectorSnapshot:
    return SectorSnapshot(
        trade_date=date.fromisoformat(trade_date),
        sector_id=sector_id,
        sector_name=sector_name,
        persistence=persistence,
        diffusion=diffusion,
        money_making=money_making,
        leader_strength=leader_strength,
        relative_strength=relative_strength,
        activity=activity,
    )


def test_mainline_sector_scorer_ranks_sectors_by_composite_score() -> None:
    snapshots = [
        build_snapshot("2025-01-03", "AI", "AI", 0.9, 0.8, 0.9, 1.0, 0.8, 0.9),
        build_snapshot("2025-01-03", "MIL", "Military", 0.5, 0.5, 0.4, 0.6, 0.5, 0.4),
    ]

    scores = MainlineSectorScorer().score(snapshots)

    assert scores[0].sector_id == "AI"
    assert scores[0].rank == 1
    assert scores[1].rank == 2
    assert scores[0].composite_score > scores[1].composite_score


def test_attack_permission_requires_segment_and_score_separation() -> None:
    snapshots = [
        build_snapshot("2025-01-03", "AI", "AI", 0.9, 0.8, 0.9, 1.0, 0.8, 0.9),
        build_snapshot("2025-01-03", "MIL", "Military", 0.5, 0.5, 0.4, 0.6, 0.5, 0.4),
        build_snapshot("2025-01-06", "AI", "AI", 0.8, 0.8, 0.7, 0.8, 0.7, 0.8),
        build_snapshot("2025-01-06", "MIL", "Military", 0.78, 0.8, 0.7, 0.8, 0.7, 0.8),
    ]
    scores = MainlineSectorScorer().score(snapshots)
    segments = SampleSegmenter(
        SegmenterConfig(min_segment_length=1, sector_score_threshold=4.0)
    ).segment_by_sector_trend(scores)

    permissions = AttackPermissionEngine(
        AttackPermissionConfig(min_top_score=4.0, min_score_margin=0.2)
    ).evaluate(scores, segments)

    assert permissions[0].is_attack_allowed is True
    assert permissions[0].approved_sector_id == "AI"
    assert permissions[1].is_attack_allowed is False
    assert permissions[1].reason == "top_score_margin_too_small"
