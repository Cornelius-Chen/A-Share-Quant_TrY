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
class MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalV1:
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
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_execution_contract_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_runtime_execution_contract_change_signal_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_runtime_execution_contract_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalV1:
        current = _read_csv(self.contract_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        runtime_consumer_mode_change = _state_change(
            current["runtime_consumer_mode"],
            previous["runtime_consumer_mode"] if previous else None,
        )
        contract_action_change = _state_change(
            current["contract_action"],
            previous["contract_action"] if previous else None,
        )
        sleep_strategy_change = _state_change(
            current["sleep_strategy_seconds"],
            previous["sleep_strategy_seconds"] if previous else None,
        )
        backoff_mode_change = _state_change(
            current["backoff_mode"],
            previous["backoff_mode"] if previous else None,
        )
        reopen_target_change = _state_change(
            current["reopen_target"],
            previous["reopen_target"] if previous else None,
        )

        row = {
            "runtime_execution_contract_change_signal_id": "internal_hot_news_program_runtime_execution_contract_change_latest",
            "runtime_consumer_mode_change": runtime_consumer_mode_change,
            "contract_action_change": contract_action_change,
            "sleep_strategy_change": sleep_strategy_change,
            "backoff_mode_change": backoff_mode_change,
            "reopen_target_change": reopen_target_change,
            "signal_priority": _signal_priority(
                [
                    runtime_consumer_mode_change,
                    contract_action_change,
                    sleep_strategy_change,
                    backoff_mode_change,
                    reopen_target_change,
                ]
            ),
            "runtime_consumer_mode_current": current["runtime_consumer_mode"],
            "contract_action_current": current["contract_action"],
            "sleep_strategy_seconds_current": current["sleep_strategy_seconds"],
            "backoff_mode_current": current["backoff_mode"],
            "reopen_target_current": current["reopen_target"],
            "delivery_state": "program_runtime_execution_contract_change_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_runtime_execution_contract_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "runtime_consumer_mode_change": runtime_consumer_mode_change,
            "contract_action_change": contract_action_change,
            "sleep_strategy_change": sleep_strategy_change,
            "backoff_mode_change": backoff_mode_change,
            "reopen_target_change": reopen_target_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_runtime_execution_contract_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
