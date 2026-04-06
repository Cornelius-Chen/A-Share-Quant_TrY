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


def _orchestration_loop_signal_mode(orchestration_mode: str, signal_priority: str) -> str:
    if orchestration_mode == "interrupt_orchestration":
        return "interrupt_orchestration_loop"
    if orchestration_mode == "tight_orchestration" or signal_priority == "p1":
        return "tight_orchestration_loop"
    return "steady_orchestration_loop"


def _reopen_target(orchestration_mode: str) -> str:
    if orchestration_mode == "interrupt_orchestration":
        return "orchestration_packet_and_scheduler_layers"
    if orchestration_mode == "tight_orchestration":
        return "orchestration_packet"
    return "none"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramOrchestrationLoopSignalFeedV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramOrchestrationLoopSignalFeedV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_packet_v1.csv"
        )
        self.change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_packet_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_loop_signal_feed_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_orchestration_loop_signal_feed_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramOrchestrationLoopSignalFeedV1:
        packet_row = _read_csv(self.packet_path)[0]
        change_signal_row = _read_csv(self.change_signal_path)[0]
        orchestration_mode = packet_row["orchestration_mode"]
        signal_priority = change_signal_row["signal_priority"]
        row = {
            "orchestration_loop_signal_id": "internal_hot_news_program_orchestration_loop_signal_latest",
            "orchestration_loop_signal_mode": _orchestration_loop_signal_mode(orchestration_mode, signal_priority),
            "orchestration_mode": orchestration_mode,
            "signal_priority": signal_priority,
            "reopen_target": _reopen_target(orchestration_mode),
            "sleep_strategy_seconds": packet_row["sleep_strategy_seconds"],
            "interrupt_required": packet_row["interrupt_required"],
            "delivery_state": "program_orchestration_loop_signal_feed_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_orchestration_loop_signal_feed",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "signal_row_count": 1,
            "orchestration_loop_signal_mode": row["orchestration_loop_signal_mode"],
            "orchestration_mode": orchestration_mode,
            "signal_priority": signal_priority,
            "reopen_target": row["reopen_target"],
            "authoritative_output": "a_share_internal_hot_news_program_orchestration_loop_signal_feed_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramOrchestrationLoopSignalFeedV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramOrchestrationLoopSignalFeedV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
