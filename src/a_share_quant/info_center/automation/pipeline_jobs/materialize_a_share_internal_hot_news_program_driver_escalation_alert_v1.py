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


def _alert_state(driver_escalation_priority: str) -> str:
    if driver_escalation_priority == "p0":
        return "high_priority_driver_escalation"
    if driver_escalation_priority == "p1":
        return "elevated_driver_escalation"
    return "no_driver_escalation"


def _consumer_instruction(driver_escalation_priority: str) -> str:
    if driver_escalation_priority == "p0":
        return "interrupt_and_reassess_program_mode_immediately"
    if driver_escalation_priority == "p1":
        return "refresh_program_mode_and_raise_attention"
    return "keep_lightweight_status_polling_only"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramDriverEscalationAlertV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramDriverEscalationAlertV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_driver_escalation_alert_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_driver_escalation_alert_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramDriverEscalationAlertV1:
        signal_row = _read_csv(self.signal_path)[0]
        driver_escalation_priority = signal_row["driver_escalation_priority"]
        alert_state = _alert_state(driver_escalation_priority)
        consumer_instruction = _consumer_instruction(driver_escalation_priority)
        row = {
            "driver_escalation_alert_id": "internal_hot_news_driver_escalation_latest",
            "driver_escalation_priority": driver_escalation_priority,
            "program_driver_transition_class": signal_row["program_driver_transition_class"],
            "program_driver_action_mode_current": signal_row["program_driver_action_mode_current"],
            "program_driver_action_mode_change": signal_row["program_driver_action_mode_change"],
            "alert_state": alert_state,
            "alert_required": str(driver_escalation_priority in {"p0", "p1"}).lower(),
            "consumer_instruction": consumer_instruction,
            "upstream_signal_priority": signal_row["signal_priority"],
            "delivery_state": "driver_escalation_alert_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_driver_escalation_alert",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "alert_row_count": 1,
            "driver_escalation_priority": driver_escalation_priority,
            "program_driver_transition_class": signal_row["program_driver_transition_class"],
            "alert_state": alert_state,
            "alert_required": row["alert_required"],
            "consumer_instruction": consumer_instruction,
            "authoritative_output": "a_share_internal_hot_news_program_driver_escalation_alert_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramDriverEscalationAlertV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramDriverEscalationAlertV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
