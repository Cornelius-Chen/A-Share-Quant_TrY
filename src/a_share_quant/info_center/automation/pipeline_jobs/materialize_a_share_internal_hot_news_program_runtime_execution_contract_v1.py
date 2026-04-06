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
        return "interrupt_loop_and_reopen_target"
    if runtime_consumer_mode == "elevate_and_reopen":
        return "elevate_and_reopen_target"
    if runtime_consumer_mode == "elevate_polling":
        return "elevate_polling_only"
    if reopen_target != "none":
        return "reopen_target_without_interrupt"
    return "keep_passive_polling"


def _sleep_strategy_seconds(suggested_poll_interval_seconds: str, runtime_attention_level: str) -> str:
    if runtime_attention_level == "high":
        return "0"
    if runtime_attention_level == "medium":
        return suggested_poll_interval_seconds
    return suggested_poll_interval_seconds


def _backoff_mode(runtime_consumer_mode: str, freshness_state: str) -> str:
    if freshness_state == "stale":
        return "force_refresh_before_next_loop"
    if runtime_consumer_mode == "passive_polling_only":
        return "steady_interval"
    return "tight_polling"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeExecutionContractV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.runtime_envelope_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_loop_runtime_envelope_v1.csv"
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
            / "a_share_internal_hot_news_program_runtime_execution_contract_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_execution_contract_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractV1:
        runtime_envelope = _read_csv(self.runtime_envelope_path)[0]
        control_packet = _read_csv(self.control_packet_path)[0]

        runtime_consumer_mode = runtime_envelope["runtime_consumer_mode"]
        suggested_poll_interval_seconds = runtime_envelope["suggested_poll_interval_seconds"]
        runtime_attention_level = runtime_envelope["runtime_attention_level"]
        reopen_target = runtime_envelope["reopen_target"]
        freshness_state = control_packet["freshness_state"]

        row = {
            "runtime_execution_contract_id": "internal_hot_news_program_runtime_execution_contract_latest",
            "runtime_consumer_mode": runtime_consumer_mode,
            "contract_action": _contract_action(runtime_consumer_mode, reopen_target),
            "interrupt_required": runtime_envelope["interrupt_required"],
            "reopen_target": reopen_target,
            "sleep_strategy_seconds": _sleep_strategy_seconds(
                suggested_poll_interval_seconds,
                runtime_attention_level,
            ),
            "suggested_poll_interval_seconds": suggested_poll_interval_seconds,
            "runtime_attention_level": runtime_attention_level,
            "backoff_mode": _backoff_mode(runtime_consumer_mode, freshness_state),
            "program_health_state": control_packet["program_health_state"],
            "freshness_state": freshness_state,
            "trading_day_state": control_packet["trading_day_state"],
            "session_phase": control_packet["session_phase"],
            "top_risk_telegraph_id": control_packet["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": control_packet["top_opportunity_telegraph_id"],
            "delivery_state": "program_runtime_execution_contract_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_execution_contract",
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
            "authoritative_output": "a_share_internal_hot_news_program_runtime_execution_contract_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeExecutionContractV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
