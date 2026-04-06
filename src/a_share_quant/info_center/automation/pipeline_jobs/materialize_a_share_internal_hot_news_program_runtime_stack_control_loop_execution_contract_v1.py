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


def _contract_action(runtime_consumer_mode: str, reopen_target: str) -> str:
    if runtime_consumer_mode == "interrupt_and_reopen":
        return "interrupt_runtime_stack_loop_and_reopen_target"
    if runtime_consumer_mode == "elevate_and_reopen":
        return "elevate_runtime_stack_loop_and_reopen_target"
    if runtime_consumer_mode == "elevate_polling":
        return "elevate_runtime_stack_polling_only"
    if reopen_target != "none":
        return "reopen_runtime_stack_target_without_interrupt"
    return "keep_runtime_stack_passive_polling"


def _backoff_mode(runtime_consumer_mode: str) -> str:
    if runtime_consumer_mode == "interrupt_and_reopen":
        return "interrupt_immediate"
    if runtime_consumer_mode in {"elevate_and_reopen", "elevate_polling"}:
        return "tight_runtime_stack_interval"
    return "steady_runtime_stack_interval"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.runtime_envelope_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_control_loop_runtime_envelope_v1.csv"
        )
        self.control_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_control_packet_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1:
        runtime_envelope = _read_csv(self.runtime_envelope_path)[0]
        control_packet = _read_csv(self.control_packet_path)[0]

        runtime_consumer_mode = runtime_envelope["runtime_consumer_mode"]
        reopen_target = runtime_envelope["reopen_target"]
        row = {
            "runtime_stack_execution_contract_id": "internal_hot_news_program_runtime_stack_control_loop_execution_contract_latest",
            "runtime_consumer_mode": runtime_consumer_mode,
            "contract_action": _contract_action(runtime_consumer_mode, reopen_target),
            "interrupt_required": runtime_envelope["interrupt_required"],
            "reopen_target": reopen_target,
            "sleep_strategy_seconds": runtime_envelope["suggested_poll_interval_seconds"],
            "suggested_poll_interval_seconds": runtime_envelope["suggested_poll_interval_seconds"],
            "runtime_attention_level": runtime_envelope["runtime_attention_level"],
            "backoff_mode": _backoff_mode(runtime_consumer_mode),
            "program_health_state": runtime_envelope["program_health_state"],
            "supervisor_mode": control_packet["supervisor_mode"],
            "supervision_loop_mode": control_packet["supervision_loop_mode"],
            "contract_signal_priority": control_packet["signal_priority"],
            "top_risk_telegraph_id": control_packet["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": control_packet["top_opportunity_telegraph_id"],
            "delivery_state": "runtime_stack_control_loop_execution_contract_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_stack_control_loop_execution_contract",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "contract_row_count": 1,
            "runtime_consumer_mode": runtime_consumer_mode,
            "contract_action": row["contract_action"],
            "sleep_strategy_seconds": row["sleep_strategy_seconds"],
            "backoff_mode": row["backoff_mode"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
