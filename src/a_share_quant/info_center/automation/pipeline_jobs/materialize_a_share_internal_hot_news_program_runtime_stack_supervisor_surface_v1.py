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


def _supervisor_mode(*, orchestration_loop_signal_mode: str, scheduler_loop_signal_mode: str, runtime_consumer_mode: str) -> str:
    if orchestration_loop_signal_mode == "interrupt_orchestration_loop":
        return "interrupt_supervision"
    if orchestration_loop_signal_mode == "tight_orchestration_loop" or scheduler_loop_signal_mode == "tight_poll_requeue":
        return "tight_supervision"
    if runtime_consumer_mode in {"interrupt_and_reopen", "elevate_and_reopen", "elevate_polling"}:
        return "elevated_supervision"
    return "steady_supervision"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.control_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.runtime_contract_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_execution_contract_v1.csv"
        )
        self.scheduler_loop_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_loop_signal_feed_v1.csv"
        )
        self.orchestration_loop_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_loop_signal_feed_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_surface_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_supervisor_surface_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1:
        control_packet = _read_csv(self.control_packet_path)[0]
        runtime_contract = _read_csv(self.runtime_contract_path)[0]
        scheduler_loop_signal = _read_csv(self.scheduler_loop_signal_path)[0]
        orchestration_loop_signal = _read_csv(self.orchestration_loop_signal_path)[0]

        supervisor_mode = _supervisor_mode(
            orchestration_loop_signal_mode=orchestration_loop_signal["orchestration_loop_signal_mode"],
            scheduler_loop_signal_mode=scheduler_loop_signal["scheduler_loop_signal_mode"],
            runtime_consumer_mode=runtime_contract["runtime_consumer_mode"],
        )

        row = {
            "runtime_stack_supervisor_id": "internal_hot_news_program_runtime_stack_supervisor_latest",
            "supervisor_mode": supervisor_mode,
            "program_health_state": control_packet["program_health_state"],
            "freshness_state": control_packet["freshness_state"],
            "trading_day_state": control_packet["trading_day_state"],
            "session_phase": control_packet["session_phase"],
            "runtime_consumer_mode": runtime_contract["runtime_consumer_mode"],
            "contract_action": runtime_contract["contract_action"],
            "scheduler_loop_signal_mode": scheduler_loop_signal["scheduler_loop_signal_mode"],
            "scheduler_signal_priority": scheduler_loop_signal["signal_priority"],
            "orchestration_loop_signal_mode": orchestration_loop_signal["orchestration_loop_signal_mode"],
            "orchestration_signal_priority": orchestration_loop_signal["signal_priority"],
            "top_risk_telegraph_id": control_packet["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": control_packet["top_opportunity_telegraph_id"],
            "delivery_state": "runtime_stack_supervisor_surface_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_supervisor_surface",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "surface_row_count": 1,
            "supervisor_mode": supervisor_mode,
            "program_health_state": row["program_health_state"],
            "runtime_consumer_mode": row["runtime_consumer_mode"],
            "scheduler_loop_signal_mode": row["scheduler_loop_signal_mode"],
            "orchestration_loop_signal_mode": row["orchestration_loop_signal_mode"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_supervisor_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
