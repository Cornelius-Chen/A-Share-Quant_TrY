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


def _driver_transition_class(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current == previous:
        return "stable"
    if previous == "watch_only" and current in {"prepare", "live_route"}:
        return "activation_rotation"
    if current == "stale_block":
        return "hard_block_rotation"
    return "noncritical_rotation"


def _driver_escalation_priority(transition_class: str) -> str:
    if transition_class == "hard_block_rotation":
        return "p0"
    if transition_class == "activation_rotation":
        return "p1"
    return "p2"


def _signal_priority(states: list[str], driver_escalation_priority: str) -> str:
    if driver_escalation_priority in {"p0", "p1"}:
        return driver_escalation_priority
    if "state_changed" in states:
        return "p1"
    return "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramStatusChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramStatusChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_surface_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_status_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_change_signal_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_status_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramStatusChangeSignalV1:
        current = _read_csv(self.status_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        program_health_state = _state_change(
            current["program_health_state"],
            previous["program_health_state"] if previous else None,
        )
        action_mode_state = _state_change(
            current["global_program_action_mode"],
            previous["global_program_action_mode"] if previous else None,
        )
        attention_state = _state_change(
            current["needs_attention"],
            previous["needs_attention"] if previous else None,
        )
        freshness_state = _state_change(
            current["freshness_state"],
            previous["freshness_state"] if previous else None,
        )
        timeout_state = _state_change(
            current["heartbeat_timeout_state"],
            previous["heartbeat_timeout_state"] if previous else None,
        )
        trading_day_state = _state_change(
            current["trading_day_state"],
            previous.get("trading_day_state") if previous else None,
        )
        session_phase_state = _state_change(
            current["session_phase"],
            previous.get("session_phase") if previous else None,
        )
        program_consumer_gate_mode_state = _state_change(
            current["program_consumer_gate_mode"],
            previous.get("program_consumer_gate_mode") if previous else None,
        )
        program_driver_action_mode_state = _state_change(
            current["program_driver_action_mode"],
            previous.get("program_driver_action_mode") if previous else None,
        )
        program_driver_transition_class = _driver_transition_class(
            current["program_driver_action_mode"],
            previous.get("program_driver_action_mode") if previous else None,
        )
        driver_escalation_priority = _driver_escalation_priority(program_driver_transition_class)

        row = {
            "status_change_signal_id": "internal_hot_news_program_status_change_latest",
            "program_health_state_change": program_health_state,
            "global_program_action_mode_change": action_mode_state,
            "needs_attention_change": attention_state,
            "trading_day_state_change": trading_day_state,
            "session_phase_change": session_phase_state,
            "program_consumer_gate_mode_change": program_consumer_gate_mode_state,
            "program_driver_action_mode_change": program_driver_action_mode_state,
            "program_driver_transition_class": program_driver_transition_class,
            "driver_escalation_priority": driver_escalation_priority,
            "freshness_state_change": freshness_state,
            "heartbeat_timeout_state_change": timeout_state,
            "signal_priority": _signal_priority(
                [
                    program_health_state,
                    action_mode_state,
                    attention_state,
                    trading_day_state,
                    session_phase_state,
                    program_consumer_gate_mode_state,
                    program_driver_action_mode_state,
                    freshness_state,
                    timeout_state,
                ],
                driver_escalation_priority,
            ),
            "program_health_state_current": current["program_health_state"],
            "global_program_action_mode_current": current["global_program_action_mode"],
            "needs_attention_current": current["needs_attention"],
            "trading_day_state_current": current["trading_day_state"],
            "session_phase_current": current["session_phase"],
            "program_consumer_gate_mode_current": current["program_consumer_gate_mode"],
            "program_driver_action_mode_current": current["program_driver_action_mode"],
            "driver_escalation_priority_current": driver_escalation_priority,
            "freshness_state_current": current["freshness_state"],
            "heartbeat_timeout_state_current": current["heartbeat_timeout_state"],
            "delivery_state": "program_status_change_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.serving_path,
            [
                {
                    "view_id": "internal_hot_news_program_status_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "program_health_state_change": program_health_state,
            "global_program_action_mode_change": action_mode_state,
            "needs_attention_change": attention_state,
            "trading_day_state_change": trading_day_state,
            "session_phase_change": session_phase_state,
            "program_consumer_gate_mode_change": program_consumer_gate_mode_state,
            "program_driver_action_mode_change": program_driver_action_mode_state,
            "program_driver_transition_class": program_driver_transition_class,
            "driver_escalation_priority": driver_escalation_priority,
            "freshness_state_change": freshness_state,
            "heartbeat_timeout_state_change": timeout_state,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_status_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramStatusChangeSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramStatusChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
