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


def _contract_action(supervision_loop_mode: str, supervisor_mode: str, reopen_target: str) -> str:
    if supervision_loop_mode == "interrupt_supervision_loop":
        return "interrupt_supervision_loop_and_reopen_target"
    if supervision_loop_mode == "tight_supervision_loop":
        return "tighten_supervision_loop"
    if supervisor_mode == "elevated_supervision":
        return "elevate_supervision_only"
    if reopen_target != "none":
        return "reopen_target_without_interrupt"
    return "keep_steady_supervision"


def _sleep_strategy_seconds(supervision_loop_mode: str) -> str:
    if supervision_loop_mode == "interrupt_supervision_loop":
        return "0"
    if supervision_loop_mode == "tight_supervision_loop":
        return "60"
    return "300"


def _backoff_mode(supervision_loop_mode: str) -> str:
    if supervision_loop_mode == "interrupt_supervision_loop":
        return "interrupt_immediate"
    if supervision_loop_mode == "tight_supervision_loop":
        return "tight_supervision_interval"
    return "steady_supervision_interval"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1:
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
        self.loop_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_v1.csv"
        )
        self.loop_change_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervision_contract_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_supervision_contract_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1:
        surface_row = _read_csv(self.surface_path)[0]
        change_row = _read_csv(self.change_signal_path)[0]
        loop_row = _read_csv(self.loop_signal_path)[0]
        loop_change_row = _read_csv(self.loop_change_path)[0]

        supervisor_mode = surface_row["supervisor_mode"]
        supervision_loop_mode = loop_row["supervision_loop_mode"]
        reopen_target = loop_row["reopen_target"]
        signal_priority = loop_change_row["signal_priority"]

        row = {
            "runtime_stack_supervision_contract_id": "internal_hot_news_program_runtime_stack_supervision_contract_latest",
            "supervisor_mode": supervisor_mode,
            "supervision_loop_mode": supervision_loop_mode,
            "contract_action": _contract_action(supervision_loop_mode, supervisor_mode, reopen_target),
            "signal_priority": signal_priority,
            "interrupt_required": "true" if supervision_loop_mode == "interrupt_supervision_loop" else "false",
            "reopen_target": reopen_target,
            "sleep_strategy_seconds": _sleep_strategy_seconds(supervision_loop_mode),
            "backoff_mode": _backoff_mode(supervision_loop_mode),
            "program_health_state": surface_row["program_health_state"],
            "runtime_consumer_mode": surface_row["runtime_consumer_mode"],
            "scheduler_loop_signal_mode": surface_row["scheduler_loop_signal_mode"],
            "orchestration_loop_signal_mode": surface_row["orchestration_loop_signal_mode"],
            "supervisor_signal_priority": change_row["signal_priority"],
            "delivery_state": "runtime_stack_supervision_contract_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_supervision_contract",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "contract_row_count": 1,
            "supervisor_mode": supervisor_mode,
            "supervision_loop_mode": supervision_loop_mode,
            "contract_action": row["contract_action"],
            "sleep_strategy_seconds": row["sleep_strategy_seconds"],
            "backoff_mode": row["backoff_mode"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_supervision_contract_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisionContractV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
