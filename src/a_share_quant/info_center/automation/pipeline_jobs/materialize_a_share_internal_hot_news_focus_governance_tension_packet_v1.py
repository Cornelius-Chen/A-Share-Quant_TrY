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


def _derive_tension_state(
    *,
    incumbent_is_leader: str,
    review_state: str,
    support_delta_vs_incumbent: int,
) -> tuple[str, str, str]:
    if incumbent_is_leader == "false" and review_state == "hold_incumbent_focus":
        return (
            "incumbent_not_leader_but_gate_holds",
            "p2",
            "leaderboard_lead_alone_not_sufficient_for_rotation",
        )
    if incumbent_is_leader == "false" and review_state == "keep_incumbent_but_raise_review_attention":
        return (
            "incumbent_not_leader_under_review_attention",
            "p2",
            "continue_review_attention_until_support_gap_expands",
        )
    if incumbent_is_leader == "false" and review_state == "open_next_rotation_review":
        return (
            "challenger_leads_and_rotation_gate_open",
            "p1",
            "prepare_rotation_review_or_shadow_promotion",
        )
    if incumbent_is_leader == "true" and support_delta_vs_incumbent == 0:
        return (
            "incumbent_holds_with_no_support_gap",
            "p3",
            "steady_monitoring_only",
        )
    return (
        "incumbent_leads_and_gate_consistent",
        "p3",
        "background_monitor_only",
    )


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsFocusGovernanceTensionPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFocusGovernanceTensionPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.leaderboard_summary_path = (
            derived_base / "a_share_internal_hot_news_focus_competition_leaderboard_summary_v1.csv"
        )
        self.review_path = (
            derived_base / "a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1.csv"
        )
        self.output_path = (
            derived_base / "a_share_internal_hot_news_focus_governance_tension_packet_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_focus_governance_tension_packet_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFocusGovernanceTensionPacketV1:
        leaderboard = _read_csv(self.leaderboard_summary_path)[0]
        review = _read_csv(self.review_path)[0]
        support_delta_vs_incumbent = int(review["support_delta_vs_incumbent"])
        tension_state, tension_priority, tension_instruction = _derive_tension_state(
            incumbent_is_leader=leaderboard["incumbent_is_leader"],
            review_state=review["review_state"],
            support_delta_vs_incumbent=support_delta_vs_incumbent,
        )

        row = {
            "focus_governance_tension_packet_id": "internal_hot_news_focus_governance_tension_latest",
            "current_primary_theme_slug": leaderboard["current_primary_theme_slug"],
            "current_primary_watch_symbol": leaderboard["current_primary_watch_symbol"],
            "current_primary_rank": leaderboard["current_primary_rank"],
            "incumbent_is_leader": leaderboard["incumbent_is_leader"],
            "leader_theme_slug": leaderboard["leader_theme_slug"],
            "leader_watch_symbol": leaderboard["leader_watch_symbol"],
            "review_state": review["review_state"],
            "review_recommendation": review["review_recommendation"],
            "support_delta_vs_incumbent": review["support_delta_vs_incumbent"],
            "tension_state": tension_state,
            "tension_priority": tension_priority,
            "tension_instruction": tension_instruction,
            "delivery_state": "focus_governance_tension_packet_ready",
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_focus_governance_tension_packet",
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
            "support_delta_vs_incumbent": int(row["support_delta_vs_incumbent"]),
            "tension_state": row["tension_state"],
            "tension_priority": row["tension_priority"],
            "tension_instruction": row["tension_instruction"],
            "authoritative_output": "a_share_internal_hot_news_focus_governance_tension_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsFocusGovernanceTensionPacketV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFocusGovernanceTensionPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
