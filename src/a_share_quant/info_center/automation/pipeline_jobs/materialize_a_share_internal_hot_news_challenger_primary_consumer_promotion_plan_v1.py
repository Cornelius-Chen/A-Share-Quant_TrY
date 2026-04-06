from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.rotation_review_path = base / "a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1.csv"
        self.shadow_change_signal_path = base / "a_share_internal_hot_news_challenger_rotation_shadow_change_signal_v1.csv"
        self.challenger_packet_path = base / "a_share_internal_hot_news_challenger_rotation_candidate_packet_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_v1.csv"
        self.summary_path = base / "a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_summary_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1:
        rotation_review = _read_csv(self.rotation_review_path)[0]
        shadow_change = _read_csv(self.shadow_change_signal_path)[0]
        challenger_packet = _read_csv(self.challenger_packet_path)[0]

        plan_rows = [
            {
                "plan_step_order": "1",
                "plan_step_id": "confirm_challenger_rotation_acceptance",
                "plan_step_state": "pending_manual_acceptance",
                "plan_step_direction": "explicitly accept the challenger p1 focus rotation before touching the current primary consumer chain",
            },
            {
                "plan_step_order": "2",
                "plan_step_id": "promote_challenger_shadow_snapshot_to_primary_snapshot",
                "plan_step_state": "blocked_by_step_1",
                "plan_step_direction": "replace current top opportunity and top watch with the challenger shadow state only after acceptance",
            },
            {
                "plan_step_order": "3",
                "plan_step_id": "propagate_challenger_rotation_into_primary_control_packet",
                "plan_step_state": "blocked_by_step_2",
                "plan_step_direction": "refresh primary control consumers after the challenger snapshot rotation becomes intentional",
            },
            {
                "plan_step_order": "4",
                "plan_step_id": "rebaseline_change_signals_after_challenger_promotion",
                "plan_step_state": "blocked_by_step_3",
                "plan_step_direction": "rebaseline symbol watch and control change signals after challenger promotion to avoid stale p1 deltas",
            },
        ]

        summary_row = {
            "plan_id": "internal_hot_news_challenger_primary_consumer_promotion_plan_latest",
            "rotation_review_state": rotation_review["review_state"],
            "shadow_change_signal_priority": shadow_change["signal_priority"],
            "challenger_top_opportunity_theme": challenger_packet["challenger_top_opportunity_theme"],
            "challenger_top_watch_symbol": challenger_packet["challenger_top_watch_symbol"],
            "plan_state": "manual_acceptance_required_before_challenger_primary_consumer_promotion",
            "plan_step_count": str(len(plan_rows)),
        }

        _write_csv(self.output_path, plan_rows)
        _write_csv(self.summary_path, [summary_row])

        summary = {
            "rotation_review_state": rotation_review["review_state"],
            "shadow_change_signal_priority": shadow_change["signal_priority"],
            "challenger_top_opportunity_theme": challenger_packet["challenger_top_opportunity_theme"],
            "challenger_top_watch_symbol": challenger_packet["challenger_top_watch_symbol"],
            "plan_state": summary_row["plan_state"],
            "plan_step_count": len(plan_rows),
            "authoritative_output": "a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1(
            summary=summary,
            rows=plan_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
