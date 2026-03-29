from __future__ import annotations

from datetime import date

from a_share_quant.common.models import StockSnapshot
from a_share_quant.strategy.theme_hierarchy_gap_analysis import ThemeHierarchyGapAnalyzer


class _Cfg:
    def __init__(self, *, min_quality: float, min_composite: float) -> None:
        self.min_quality_for_late_mover = min_quality
        self.min_composite_for_non_junk = min_composite


class _Assignment:
    def __init__(self, *, layer: str, reason: str, layer_score: float, leader: float, core: float, late: float) -> None:
        self.layer = layer
        self.reason = reason
        self.layer_score = layer_score
        self.leader_score = leader
        self.core_score = core
        self.late_score = late


def test_theme_hierarchy_gap_flags_threshold_band_blockers() -> None:
    analyzer = ThemeHierarchyGapAnalyzer()
    snapshot = StockSnapshot(
        trade_date=date(2024, 9, 26),
        symbol="AAA",
        sector_id="BK1173",
        sector_name="Theme",
        expected_upside=0.6,
        drive_strength=0.6,
        stability=0.5,
        liquidity=0.1,
        late_mover_quality=0.56,
        resonance=0.62,
    )
    incumbent_assignment = _Assignment(
        layer="late_mover",
        reason="late_mover_quality_fallback",
        layer_score=0.61,
        leader=0.58,
        core=0.40,
        late=0.61,
    )
    challenger_assignment = _Assignment(
        layer="junk",
        reason="fallback_to_junk",
        layer_score=0.61,
        leader=0.58,
        core=0.40,
        late=0.61,
    )

    flags = analyzer._blocker_flags(
        snapshot=snapshot,
        challenger_assignment=challenger_assignment,
        incumbent_assignment=incumbent_assignment,
        challenger_cfg=_Cfg(min_quality=0.60, min_composite=0.57),
        incumbent_cfg=_Cfg(min_quality=0.55, min_composite=0.55),
    )

    assert "late_quality_below_challenger_threshold" in flags
    assert "late_quality_in_incumbent_only_band" in flags
    assert "fallback_to_junk_path" in flags
    assert "incumbent_used_late_mover_fallback" in flags
