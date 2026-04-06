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


def _derive_readiness(
    *,
    review_state: str,
    tension_state: str,
    tension_priority: str,
    attention_priority: str,
    incumbent_is_leader: str,
) -> tuple[str, str, str]:
    if review_state == "open_next_rotation_review":
        return (
            "rotation_review_open_now",
            "p1",
            "prepare_shadow_promotion_or_acceptance_decision",
        )
    if incumbent_is_leader == "false" and tension_priority == "p2":
        return (
            "rank_misaligned_under_gate_hold",
            "p2",
            "keep_incumbent_and_monitor_for_gap_expansion",
        )
    if tension_state == "incumbent_not_leader_but_gate_holds":
        return (
            "governance_hold_despite_rank_loss",
            "p2",
            "do_not_rotate_on_rank_alone",
        )
    if attention_priority == "p3" and incumbent_is_leader == "true":
        return (
            "steady_background_monitoring_only",
            "p3",
            "maintain_current_focus_and_background_monitoring",
        )
    return (
        "hold_current_focus_pending_new_evidence",
        "p3",
        "continue_regular_review_polling",
    )


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsFocusRotationReadinessPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFocusRotationReadinessPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.leaderboard_summary_path = (
            base / "a_share_internal_hot_news_focus_competition_leaderboard_summary_v1.csv"
        )
        self.review_attention_path = (
            base / "a_share_internal_hot_news_challenger_review_attention_packet_v1.csv"
        )
        self.governance_tension_path = (
            base / "a_share_internal_hot_news_focus_governance_tension_packet_v1.csv"
        )
        self.output_path = (
            base / "a_share_internal_hot_news_focus_rotation_readiness_packet_v1.csv"
        )
        self.registry_path = (
            serving / "a_share_internal_hot_news_focus_rotation_readiness_packet_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFocusRotationReadinessPacketV1:
        leaderboard = _read_csv(self.leaderboard_summary_path)[0]
        review_attention = _read_csv(self.review_attention_path)[0]
        governance_tension = _read_csv(self.governance_tension_path)[0]

        readiness_state, readiness_priority, readiness_instruction = _derive_readiness(
            review_state=review_attention["review_state"],
            tension_state=governance_tension["tension_state"],
            tension_priority=governance_tension["tension_priority"],
            attention_priority=review_attention["attention_priority"],
            incumbent_is_leader=leaderboard["incumbent_is_leader"],
        )

        row = {
            "focus_rotation_readiness_packet_id": "internal_hot_news_focus_rotation_readiness_latest",
            "current_primary_theme_slug": leaderboard["current_primary_theme_slug"],
            "current_primary_watch_symbol": leaderboard["current_primary_watch_symbol"],
            "current_primary_rank": leaderboard["current_primary_rank"],
            "incumbent_is_leader": leaderboard["incumbent_is_leader"],
            "leader_theme_slug": leaderboard["leader_theme_slug"],
            "leader_watch_symbol": leaderboard["leader_watch_symbol"],
            "review_state": review_attention["review_state"],
            "attention_priority": review_attention["attention_priority"],
            "tension_state": governance_tension["tension_state"],
            "tension_priority": governance_tension["tension_priority"],
            "rotation_readiness_state": readiness_state,
            "rotation_readiness_priority": readiness_priority,
            "rotation_readiness_instruction": readiness_instruction,
            "delivery_state": "focus_rotation_readiness_packet_ready",
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_focus_rotation_readiness_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "current_primary_theme_slug": row["current_primary_theme_slug"],
            "current_primary_rank": int(row["current_primary_rank"]),
            "incumbent_is_leader": row["incumbent_is_leader"],
            "leader_theme_slug": row["leader_theme_slug"],
            "review_state": row["review_state"],
            "tension_state": row["tension_state"],
            "rotation_readiness_state": row["rotation_readiness_state"],
            "rotation_readiness_priority": row["rotation_readiness_priority"],
            "rotation_readiness_instruction": row["rotation_readiness_instruction"],
            "authoritative_output": "a_share_internal_hot_news_focus_rotation_readiness_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsFocusRotationReadinessPacketV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFocusRotationReadinessPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
