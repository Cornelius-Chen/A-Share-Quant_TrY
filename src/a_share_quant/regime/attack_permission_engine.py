from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from a_share_quant.common.models import AttackPermission, MainlineSectorScore, SampleSegment


@dataclass(frozen=True, slots=True)
class AttackPermissionConfig:
    min_top_score: float = 4.0
    min_score_margin: float = 0.2
    require_active_segment: bool = True


class AttackPermissionEngine:
    """Approve offensive participation only when both environment and mainline quality are acceptable."""

    def __init__(self, config: AttackPermissionConfig | None = None) -> None:
        self.config = config or AttackPermissionConfig()

    def evaluate(
        self,
        sector_scores: list[MainlineSectorScore],
        segments: list[SampleSegment],
    ) -> list[AttackPermission]:
        scores_by_date = self._scores_by_date(sector_scores)
        active_dates = self._active_dates(segments)
        permissions: list[AttackPermission] = []

        for trade_date in sorted(scores_by_date):
            ranked = scores_by_date[trade_date]
            top_score = ranked[0]
            second_score = ranked[1] if len(ranked) > 1 else None
            in_segment = trade_date in active_dates

            if self.config.require_active_segment and not in_segment:
                permissions.append(
                    AttackPermission(
                        trade_date=trade_date,
                        is_attack_allowed=False,
                        approved_sector_id=None,
                        approved_sector_name=None,
                        score=None,
                        reason="outside_segment",
                    )
                )
                continue

            if top_score.composite_score < self.config.min_top_score:
                permissions.append(
                    AttackPermission(
                        trade_date=trade_date,
                        is_attack_allowed=False,
                        approved_sector_id=None,
                        approved_sector_name=None,
                        score=top_score.composite_score,
                        reason="top_score_below_threshold",
                    )
                )
                continue

            if second_score is not None:
                margin = top_score.composite_score - second_score.composite_score
                if margin < self.config.min_score_margin:
                    permissions.append(
                        AttackPermission(
                            trade_date=trade_date,
                            is_attack_allowed=False,
                            approved_sector_id=None,
                            approved_sector_name=None,
                            score=top_score.composite_score,
                            reason="top_score_margin_too_small",
                        )
                    )
                    continue

            permissions.append(
                AttackPermission(
                    trade_date=trade_date,
                    is_attack_allowed=True,
                    approved_sector_id=top_score.sector_id,
                    approved_sector_name=top_score.sector_name,
                    score=top_score.composite_score,
                    reason="approved",
                )
            )

        return permissions

    def _scores_by_date(
        self,
        sector_scores: list[MainlineSectorScore],
    ) -> dict[date, list[MainlineSectorScore]]:
        grouped: dict[date, list[MainlineSectorScore]] = {}
        for score in sector_scores:
            grouped.setdefault(score.trade_date, []).append(score)
        for trade_date in grouped:
            grouped[trade_date].sort(key=lambda item: item.rank)
        return grouped

    def _active_dates(self, segments: list[SampleSegment]) -> set[date]:
        active_dates: set[date] = set()
        for segment in segments:
            current = segment.start_date
            while current <= segment.end_date:
                active_dates.add(current)
                current = date.fromordinal(current.toordinal() + 1)
        return active_dates
