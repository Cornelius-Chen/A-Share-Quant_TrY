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


def _supervision_loop_mode(supervisor_mode: str, signal_priority: str) -> str:
    if supervisor_mode == "interrupt_supervision":
        return "interrupt_supervision_loop"
    if supervisor_mode in {"tight_supervision", "elevated_supervision"} or signal_priority == "p1":
        return "tight_supervision_loop"
    return "steady_supervision_loop"


def _reopen_target(supervisor_mode: str) -> str:
    if supervisor_mode == "interrupt_supervision":
        return "supervisor_surface_and_lower_stacks"
    if supervisor_mode in {"tight_supervision", "elevated_supervision"}:
        return "supervisor_surface"
    return "none"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_surface_v1.csv"
        )
        self.change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedV1:
        surface_row = _read_csv(self.surface_path)[0]
        change_signal_row = _read_csv(self.change_signal_path)[0]
        supervisor_mode = surface_row["supervisor_mode"]
        signal_priority = change_signal_row["signal_priority"]
        row = {
            "runtime_stack_supervisor_loop_signal_id": "internal_hot_news_program_runtime_stack_supervisor_loop_signal_latest",
            "supervision_loop_mode": _supervision_loop_mode(supervisor_mode, signal_priority),
            "supervisor_mode": supervisor_mode,
            "signal_priority": signal_priority,
            "reopen_target": _reopen_target(supervisor_mode),
            "program_health_state": surface_row["program_health_state"],
            "delivery_state": "runtime_stack_supervisor_loop_signal_feed_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "signal_row_count": 1,
            "supervision_loop_mode": row["supervision_loop_mode"],
            "supervisor_mode": supervisor_mode,
            "signal_priority": signal_priority,
            "reopen_target": row["reopen_target"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
