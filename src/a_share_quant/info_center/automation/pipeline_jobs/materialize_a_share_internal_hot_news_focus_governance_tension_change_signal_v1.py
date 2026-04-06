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


def _state_change(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current != previous:
        return "state_changed"
    return "stable"


def _signal_priority(states: list[str]) -> str:
    return "p1" if "state_changed" in states else "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.packet_path = base / "a_share_internal_hot_news_focus_governance_tension_packet_v1.csv"
        self.history_path = (
            serving / "a_share_internal_hot_news_focus_governance_tension_packet_history_v1.csv"
        )
        self.output_path = (
            base / "a_share_internal_hot_news_focus_governance_tension_change_signal_v1.csv"
        )
        self.registry_path = (
            serving / "a_share_internal_hot_news_focus_governance_tension_change_signal_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1:
        current = _read_csv(self.packet_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        current_primary_rank_change = _state_change(
            current["current_primary_rank"],
            previous.get("current_primary_rank") if previous else None,
        )
        incumbent_is_leader_change = _state_change(
            current["incumbent_is_leader"],
            previous.get("incumbent_is_leader") if previous else None,
        )
        review_state_change = _state_change(
            current["review_state"],
            previous.get("review_state") if previous else None,
        )
        tension_state_change = _state_change(
            current["tension_state"],
            previous.get("tension_state") if previous else None,
        )
        tension_priority_change = _state_change(
            current["tension_priority"],
            previous.get("tension_priority") if previous else None,
        )

        row = {
            "focus_governance_tension_change_signal_id": "internal_hot_news_focus_governance_tension_change_latest",
            "current_primary_rank_change": current_primary_rank_change,
            "incumbent_is_leader_change": incumbent_is_leader_change,
            "review_state_change": review_state_change,
            "tension_state_change": tension_state_change,
            "tension_priority_change": tension_priority_change,
            "signal_priority": _signal_priority(
                [
                    current_primary_rank_change,
                    incumbent_is_leader_change,
                    review_state_change,
                    tension_state_change,
                    tension_priority_change,
                ]
            ),
            "current_primary_rank_current": current["current_primary_rank"],
            "incumbent_is_leader_current": current["incumbent_is_leader"],
            "review_state_current": current["review_state"],
            "tension_state_current": current["tension_state"],
            "tension_priority_current": current["tension_priority"],
            "delivery_state": "focus_governance_tension_change_signal_ready",
        }

        _write_csv(self.output_path, [row])
        _write_csv(self.history_path, [current])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_focus_governance_tension_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "current_primary_rank_change": current_primary_rank_change,
            "incumbent_is_leader_change": incumbent_is_leader_change,
            "review_state_change": review_state_change,
            "tension_state_change": tension_state_change,
            "tension_priority_change": tension_priority_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_focus_governance_tension_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
