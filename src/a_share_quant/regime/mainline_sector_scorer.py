from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.common.models import MainlineSectorScore, SectorSnapshot


@dataclass(frozen=True, slots=True)
class MainlineSectorScorer:
    persistence_weight: float = 1.0
    diffusion_weight: float = 1.0
    money_making_weight: float = 1.0
    leader_strength_weight: float = 1.0
    relative_strength_weight: float = 1.0
    activity_weight: float = 1.0

    def score(self, snapshots: list[SectorSnapshot]) -> list[MainlineSectorScore]:
        """Score sectors by day using the V1 candidate dimensions from the protocol."""
        grouped: dict[date, list[SectorSnapshot]] = {}
        for snapshot in snapshots:
            grouped.setdefault(snapshot.trade_date, []).append(snapshot)

        all_scores: list[MainlineSectorScore] = []
        for trade_date in sorted(grouped):
            day_snapshots = grouped[trade_date]
            ranked = sorted(
                day_snapshots,
                key=self._composite_score,
                reverse=True,
            )
            for index, snapshot in enumerate(ranked, start=1):
                all_scores.append(
                    MainlineSectorScore(
                        trade_date=snapshot.trade_date,
                        sector_id=snapshot.sector_id,
                        sector_name=snapshot.sector_name,
                        composite_score=round(self._composite_score(snapshot), 6),
                        rank=index,
                        persistence=snapshot.persistence,
                        diffusion=snapshot.diffusion,
                        money_making=snapshot.money_making,
                        leader_strength=snapshot.leader_strength,
                        relative_strength=snapshot.relative_strength,
                        activity=snapshot.activity,
                    )
                )
        return all_scores

    def top_sector_by_date(
        self,
        snapshots: list[SectorSnapshot],
    ) -> dict[date, MainlineSectorScore]:
        """Return the top-ranked sector score for each trading day."""
        top_by_date: dict[date, MainlineSectorScore] = {}
        for score in self.score(snapshots):
            top_by_date.setdefault(score.trade_date, score)
        return top_by_date

    def _composite_score(self, snapshot: SectorSnapshot) -> float:
        return (
            snapshot.persistence * self.persistence_weight
            + snapshot.diffusion * self.diffusion_weight
            + snapshot.money_making * self.money_making_weight
            + snapshot.leader_strength * self.leader_strength_weight
            + snapshot.relative_strength * self.relative_strength_weight
            + snapshot.activity * self.activity_weight
        )
