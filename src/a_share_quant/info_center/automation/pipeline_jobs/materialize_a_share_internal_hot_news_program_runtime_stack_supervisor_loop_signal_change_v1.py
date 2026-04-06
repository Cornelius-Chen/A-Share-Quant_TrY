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
class MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeV1:
        current = _read_csv(self.signal_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        supervision_loop_mode_change = _state_change(
            current["supervision_loop_mode"],
            previous["supervision_loop_mode"] if previous else None,
        )
        signal_priority_change = _state_change(
            current["signal_priority"],
            previous["signal_priority"] if previous else None,
        )
        reopen_target_change = _state_change(
            current["reopen_target"],
            previous["reopen_target"] if previous else None,
        )

        row = {
            "runtime_stack_supervisor_loop_signal_change_id": "internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_latest",
            "supervision_loop_mode_change": supervision_loop_mode_change,
            "signal_priority_change": signal_priority_change,
            "reopen_target_change": reopen_target_change,
            "signal_priority": _signal_priority(
                [
                    supervision_loop_mode_change,
                    signal_priority_change,
                    reopen_target_change,
                ]
            ),
            "supervision_loop_mode_current": current["supervision_loop_mode"],
            "signal_priority_current": current["signal_priority"],
            "reopen_target_current": current["reopen_target"],
            "delivery_state": "runtime_stack_supervisor_loop_signal_change_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_supervisor_loop_signal_change",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "supervision_loop_mode_change": supervision_loop_mode_change,
            "signal_priority_change": signal_priority_change,
            "reopen_target_change": reopen_target_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
