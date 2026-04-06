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


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeStackControlPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackControlPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervisor_surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_surface_v1.csv"
        )
        self.supervision_contract_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervision_contract_v1.csv"
        )
        self.supervision_contract_change_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervision_contract_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_control_packet_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_control_packet_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackControlPacketV1:
        surface_row = _read_csv(self.supervisor_surface_path)[0]
        contract_row = _read_csv(self.supervision_contract_path)[0]
        change_row = _read_csv(self.supervision_contract_change_path)[0]

        row = {
            "runtime_stack_control_packet_id": "internal_hot_news_program_runtime_stack_control_packet_latest",
            "program_health_state": surface_row["program_health_state"],
            "supervisor_mode": contract_row["supervisor_mode"],
            "supervision_loop_mode": contract_row["supervision_loop_mode"],
            "contract_action": contract_row["contract_action"],
            "interrupt_required": contract_row["interrupt_required"],
            "signal_priority": change_row["signal_priority"],
            "sleep_strategy_seconds": contract_row["sleep_strategy_seconds"],
            "backoff_mode": contract_row["backoff_mode"],
            "reopen_target": contract_row["reopen_target"],
            "runtime_consumer_mode": contract_row["runtime_consumer_mode"],
            "scheduler_loop_signal_mode": contract_row["scheduler_loop_signal_mode"],
            "orchestration_loop_signal_mode": contract_row["orchestration_loop_signal_mode"],
            "top_risk_telegraph_id": surface_row["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": surface_row["top_opportunity_telegraph_id"],
            "delivery_state": "runtime_stack_control_packet_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_control_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "program_health_state": row["program_health_state"],
            "supervisor_mode": row["supervisor_mode"],
            "supervision_loop_mode": row["supervision_loop_mode"],
            "contract_action": row["contract_action"],
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_control_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackControlPacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackControlPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
