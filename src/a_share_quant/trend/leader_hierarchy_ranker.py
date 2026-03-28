from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.common.models import HierarchyAssignment, StockSnapshot


@dataclass(frozen=True, slots=True)
class HierarchyConfig:
    min_resonance_for_core: float = 0.55
    min_quality_for_late_mover: float = 0.55
    min_composite_for_non_junk: float = 0.60


class LeaderHierarchyRanker:
    """Classify stocks inside a mainline candidate set into protocol v1.0 layers."""

    def __init__(self, config: HierarchyConfig | None = None) -> None:
        self.config = config or HierarchyConfig()

    def rank(
        self,
        snapshots: list[StockSnapshot],
        *,
        allowed_sector_ids: set[str] | None = None,
    ) -> list[HierarchyAssignment]:
        grouped: dict[tuple[date, str], list[StockSnapshot]] = {}
        for snapshot in snapshots:
            if allowed_sector_ids is not None and snapshot.sector_id not in allowed_sector_ids:
                continue
            grouped.setdefault((snapshot.trade_date, snapshot.sector_id), []).append(snapshot)

        assignments: list[HierarchyAssignment] = []
        for _, sector_snapshots in sorted(grouped.items(), key=lambda item: item[0]):
            scored = []
            for snapshot in sector_snapshots:
                leader_score = self._leader_score(snapshot)
                core_score = self._core_score(snapshot)
                late_score = self._late_score(snapshot)
                scored.append((snapshot, leader_score, core_score, late_score))

            if not scored:
                continue

            leader_symbol = max(scored, key=lambda item: item[1])[0].symbol
            core_symbol = max(
                (item for item in scored if item[0].symbol != leader_symbol),
                key=lambda item: item[2],
                default=None,
            )
            late_symbol = max(
                (item for item in scored if item[0].symbol not in {leader_symbol, core_symbol[0].symbol if core_symbol else ""}),
                key=lambda item: item[3],
                default=None,
            )

            for snapshot, leader_score, core_score, late_score in scored:
                layer, layer_score, reason = self._assign_layer(
                    snapshot,
                    leader_symbol=leader_symbol,
                    core_symbol=core_symbol[0].symbol if core_symbol else None,
                    late_symbol=late_symbol[0].symbol if late_symbol else None,
                    leader_score=leader_score,
                    core_score=core_score,
                    late_score=late_score,
                )
                assignments.append(
                    HierarchyAssignment(
                        trade_date=snapshot.trade_date,
                        symbol=snapshot.symbol,
                        sector_id=snapshot.sector_id,
                        sector_name=snapshot.sector_name,
                        layer=layer,
                        layer_score=round(layer_score, 6),
                        leader_score=round(leader_score, 6),
                        core_score=round(core_score, 6),
                        late_score=round(late_score, 6),
                        reason=reason,
                    )
                )
        return assignments

    def _assign_layer(
        self,
        snapshot: StockSnapshot,
        *,
        leader_symbol: str,
        core_symbol: str | None,
        late_symbol: str | None,
        leader_score: float,
        core_score: float,
        late_score: float,
    ) -> tuple[str, float, str]:
        max_score = max(leader_score, core_score, late_score)
        if max_score < self.config.min_composite_for_non_junk or snapshot.resonance < 0.40:
            return ("junk", max_score, "low_composite_or_low_resonance")
        if snapshot.symbol == leader_symbol:
            return ("leader", leader_score, "highest_leader_score")
        if core_symbol is not None and snapshot.symbol == core_symbol and snapshot.resonance >= self.config.min_resonance_for_core:
            return ("core", core_score, "highest_core_score")
        if late_symbol is not None and snapshot.symbol == late_symbol and snapshot.late_mover_quality >= self.config.min_quality_for_late_mover:
            return ("late_mover", late_score, "highest_late_mover_score")
        if core_score >= late_score and snapshot.resonance >= self.config.min_resonance_for_core:
            return ("core", core_score, "core_resonance_fallback")
        if snapshot.late_mover_quality >= self.config.min_quality_for_late_mover:
            return ("late_mover", late_score, "late_mover_quality_fallback")
        return ("junk", max_score, "fallback_to_junk")

    def _leader_score(self, snapshot: StockSnapshot) -> float:
        return (
            0.45 * snapshot.expected_upside
            + 0.35 * snapshot.drive_strength
            + 0.20 * snapshot.resonance
        )

    def _core_score(self, snapshot: StockSnapshot) -> float:
        return (
            0.40 * snapshot.stability
            + 0.35 * snapshot.liquidity
            + 0.25 * snapshot.resonance
        )

    def _late_score(self, snapshot: StockSnapshot) -> float:
        return (
            0.40 * snapshot.late_mover_quality
            + 0.30 * snapshot.expected_upside
            + 0.30 * snapshot.resonance
        )
