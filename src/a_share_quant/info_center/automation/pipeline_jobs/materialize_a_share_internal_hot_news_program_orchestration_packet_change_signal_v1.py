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


def _state_change(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current != previous:
        return "state_changed"
    return "stable"


def _signal_priority(states: list[str]) -> str:
    if "state_changed" in states:
        return "p1"
    return "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramOrchestrationPacketChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramOrchestrationPacketChangeSignalV1:
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
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_orchestration_packet_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_packet_change_signal_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_orchestration_packet_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramOrchestrationPacketChangeSignalV1:
        current = _read_csv(self.packet_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        orchestration_mode_change = _state_change(
            current["orchestration_mode"],
            previous["orchestration_mode"] if previous else None,
        )
        scheduler_loop_signal_mode_change = _state_change(
            current["scheduler_loop_signal_mode"],
            previous["scheduler_loop_signal_mode"] if previous else None,
        )
        runtime_consumer_mode_change = _state_change(
            current["runtime_consumer_mode"],
            previous["runtime_consumer_mode"] if previous else None,
        )
        sleep_strategy_change = _state_change(
            current["sleep_strategy_seconds"],
            previous["sleep_strategy_seconds"] if previous else None,
        )
        interrupt_required_change = _state_change(
            current["interrupt_required"],
            previous["interrupt_required"] if previous else None,
        )

        row = {
            "orchestration_packet_change_signal_id": "internal_hot_news_program_orchestration_packet_change_latest",
            "orchestration_mode_change": orchestration_mode_change,
            "scheduler_loop_signal_mode_change": scheduler_loop_signal_mode_change,
            "runtime_consumer_mode_change": runtime_consumer_mode_change,
            "sleep_strategy_change": sleep_strategy_change,
            "interrupt_required_change": interrupt_required_change,
            "signal_priority": _signal_priority(
                [
                    orchestration_mode_change,
                    scheduler_loop_signal_mode_change,
                    runtime_consumer_mode_change,
                    sleep_strategy_change,
                    interrupt_required_change,
                ]
            ),
            "orchestration_mode_current": current["orchestration_mode"],
            "scheduler_loop_signal_mode_current": current["scheduler_loop_signal_mode"],
            "runtime_consumer_mode_current": current["runtime_consumer_mode"],
            "sleep_strategy_seconds_current": current["sleep_strategy_seconds"],
            "interrupt_required_current": current["interrupt_required"],
            "delivery_state": "program_orchestration_packet_change_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_orchestration_packet_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "orchestration_mode_change": orchestration_mode_change,
            "scheduler_loop_signal_mode_change": scheduler_loop_signal_mode_change,
            "runtime_consumer_mode_change": runtime_consumer_mode_change,
            "sleep_strategy_change": sleep_strategy_change,
            "interrupt_required_change": interrupt_required_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_orchestration_packet_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramOrchestrationPacketChangeSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramOrchestrationPacketChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
