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


def _orchestration_mode(*, scheduler_loop_signal_mode: str, runtime_consumer_mode: str) -> str:
    if scheduler_loop_signal_mode == "interrupt_requeue":
        return "interrupt_orchestration"
    if scheduler_loop_signal_mode == "tight_poll_requeue" or runtime_consumer_mode in {
        "interrupt_and_reopen",
        "elevate_and_reopen",
        "elevate_polling",
    }:
        return "tight_orchestration"
    return "steady_orchestration"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramOrchestrationPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramOrchestrationPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.scheduler_loop_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_scheduler_loop_signal_feed_v1.csv"
        )
        self.runtime_contract_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_execution_contract_v1.csv"
        )
        self.control_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_orchestration_packet_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_orchestration_packet_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramOrchestrationPacketV1:
        scheduler_signal = _read_csv(self.scheduler_loop_signal_path)[0]
        runtime_contract = _read_csv(self.runtime_contract_path)[0]
        control_packet = _read_csv(self.control_packet_path)[0]

        orchestration_mode = _orchestration_mode(
            scheduler_loop_signal_mode=scheduler_signal["scheduler_loop_signal_mode"],
            runtime_consumer_mode=runtime_contract["runtime_consumer_mode"],
        )

        row = {
            "orchestration_packet_id": "internal_hot_news_program_orchestration_packet_latest",
            "orchestration_mode": orchestration_mode,
            "scheduler_loop_signal_mode": scheduler_signal["scheduler_loop_signal_mode"],
            "scheduler_mode": scheduler_signal["scheduler_mode"],
            "runtime_consumer_mode": runtime_contract["runtime_consumer_mode"],
            "contract_action": runtime_contract["contract_action"],
            "sleep_strategy_seconds": runtime_contract["sleep_strategy_seconds"],
            "reschedule_target": scheduler_signal["reschedule_target"],
            "interrupt_required": scheduler_signal["interrupt_required"],
            "program_health_state": control_packet["program_health_state"],
            "freshness_state": control_packet["freshness_state"],
            "trading_day_state": control_packet["trading_day_state"],
            "session_phase": control_packet["session_phase"],
            "top_risk_telegraph_id": control_packet["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": control_packet["top_opportunity_telegraph_id"],
            "delivery_state": "program_orchestration_packet_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_orchestration_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "orchestration_mode": orchestration_mode,
            "scheduler_loop_signal_mode": row["scheduler_loop_signal_mode"],
            "runtime_consumer_mode": row["runtime_consumer_mode"],
            "sleep_strategy_seconds": row["sleep_strategy_seconds"],
            "authoritative_output": "a_share_internal_hot_news_program_orchestration_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramOrchestrationPacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramOrchestrationPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
