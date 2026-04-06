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


def _scheduler_loop_signal_mode(scheduler_mode: str, signal_priority: str) -> str:
    if scheduler_mode == "interrupt_and_requeue":
        return "interrupt_requeue"
    if scheduler_mode == "tight_requeue" or signal_priority == "p1":
        return "tight_poll_requeue"
    return "steady_polling"


def _reschedule_target(scheduler_mode: str) -> str:
    if scheduler_mode == "interrupt_and_requeue":
        return "scheduler_queue_and_runtime_loop"
    if scheduler_mode == "tight_requeue":
        return "scheduler_queue"
    return "none"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSchedulerLoopSignalFeedV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSchedulerLoopSignalFeedV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_packet_v1.csv"
        )
        self.change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_packet_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_loop_signal_feed_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_scheduler_loop_signal_feed_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSchedulerLoopSignalFeedV1:
        packet_row = _read_csv(self.packet_path)[0]
        change_signal_row = _read_csv(self.change_signal_path)[0]
        scheduler_mode = packet_row["scheduler_mode"]
        signal_priority = change_signal_row["signal_priority"]
        row = {
            "scheduler_loop_signal_id": "internal_hot_news_program_scheduler_loop_signal_latest",
            "scheduler_loop_signal_mode": _scheduler_loop_signal_mode(scheduler_mode, signal_priority),
            "scheduler_mode": scheduler_mode,
            "signal_priority": signal_priority,
            "reschedule_target": _reschedule_target(scheduler_mode),
            "sleep_strategy_seconds": packet_row["sleep_strategy_seconds"],
            "interrupt_required": packet_row["interrupt_required"],
            "delivery_state": "program_scheduler_loop_signal_feed_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_scheduler_loop_signal_feed",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "signal_row_count": 1,
            "scheduler_loop_signal_mode": row["scheduler_loop_signal_mode"],
            "scheduler_mode": scheduler_mode,
            "signal_priority": signal_priority,
            "reschedule_target": row["reschedule_target"],
            "authoritative_output": "a_share_internal_hot_news_program_scheduler_loop_signal_feed_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSchedulerLoopSignalFeedV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSchedulerLoopSignalFeedV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
