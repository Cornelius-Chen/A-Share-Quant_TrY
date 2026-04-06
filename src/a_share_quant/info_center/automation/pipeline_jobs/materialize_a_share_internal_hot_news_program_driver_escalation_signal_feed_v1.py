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


def _interrupt_required(driver_escalation_priority: str) -> str:
    return str(driver_escalation_priority == "p0").lower()


def _signal_feed_mode(driver_escalation_priority: str) -> str:
    if driver_escalation_priority == "p0":
        return "interrupt"
    if driver_escalation_priority == "p1":
        return "elevate_attention"
    return "passive_polling"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramDriverEscalationSignalFeedV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramDriverEscalationSignalFeedV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.alert_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_driver_escalation_alert_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_driver_escalation_signal_feed_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_driver_escalation_signal_feed_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramDriverEscalationSignalFeedV1:
        alert_row = _read_csv(self.alert_path)[0]
        driver_escalation_priority = alert_row["driver_escalation_priority"]
        signal_feed_mode = _signal_feed_mode(driver_escalation_priority)
        row = {
            "driver_escalation_signal_id": "internal_hot_news_driver_escalation_signal_latest",
            "driver_escalation_priority": driver_escalation_priority,
            "signal_feed_mode": signal_feed_mode,
            "interrupt_required": _interrupt_required(driver_escalation_priority),
            "consumer_instruction": alert_row["consumer_instruction"],
            "alert_state": alert_row["alert_state"],
            "program_driver_transition_class": alert_row["program_driver_transition_class"],
            "program_driver_action_mode_current": alert_row["program_driver_action_mode_current"],
            "delivery_state": "driver_escalation_signal_feed_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_driver_escalation_signal_feed",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "signal_row_count": 1,
            "driver_escalation_priority": driver_escalation_priority,
            "signal_feed_mode": signal_feed_mode,
            "interrupt_required": row["interrupt_required"],
            "alert_state": alert_row["alert_state"],
            "authoritative_output": "a_share_internal_hot_news_program_driver_escalation_signal_feed_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramDriverEscalationSignalFeedV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramDriverEscalationSignalFeedV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
