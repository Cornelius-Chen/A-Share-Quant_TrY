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


def _scheduler_mode(contract_action: str, signal_priority: str) -> str:
    if contract_action == "interrupt_loop_and_reopen_target":
        return "interrupt_and_requeue"
    if signal_priority == "p1" or contract_action in {
        "elevate_and_reopen_target",
        "elevate_polling_only",
        "reopen_target_without_interrupt",
    }:
        return "tight_requeue"
    return "steady_schedule"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSchedulerPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSchedulerPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.contract_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_execution_contract_v1.csv"
        )
        self.change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_execution_contract_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_packet_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_scheduler_packet_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSchedulerPacketV1:
        contract_row = _read_csv(self.contract_path)[0]
        change_row = _read_csv(self.change_signal_path)[0]

        scheduler_mode = _scheduler_mode(
            contract_row["contract_action"],
            change_row["signal_priority"],
        )
        row = {
            "scheduler_packet_id": "internal_hot_news_program_scheduler_packet_latest",
            "scheduler_mode": scheduler_mode,
            "contract_action": contract_row["contract_action"],
            "runtime_consumer_mode": contract_row["runtime_consumer_mode"],
            "sleep_strategy_seconds": contract_row["sleep_strategy_seconds"],
            "backoff_mode": contract_row["backoff_mode"],
            "interrupt_required": contract_row["interrupt_required"],
            "reopen_target": contract_row["reopen_target"],
            "contract_change_signal_priority": change_row["signal_priority"],
            "contract_action_change": change_row["contract_action_change"],
            "runtime_consumer_mode_change": change_row["runtime_consumer_mode_change"],
            "delivery_state": "program_scheduler_packet_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_scheduler_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "scheduler_mode": scheduler_mode,
            "contract_action": row["contract_action"],
            "sleep_strategy_seconds": row["sleep_strategy_seconds"],
            "contract_change_signal_priority": row["contract_change_signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_scheduler_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSchedulerPacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSchedulerPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
