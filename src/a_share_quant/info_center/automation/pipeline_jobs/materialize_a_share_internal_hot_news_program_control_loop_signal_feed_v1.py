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


def _loop_signal_mode(signal_priority: str, interrupt_required_current: str) -> str:
    if interrupt_required_current == "true":
        return "interrupt"
    if signal_priority == "p1":
        return "elevate_attention"
    return "passive_polling"


def _reopen_target(row: dict[str, str]) -> str:
    if row["interrupt_required_current"] == "true":
        return "control_packet_and_driver_signal"
    if row["program_driver_signal_mode_change"] == "state_changed":
        return "control_packet"
    if row["top_risk_reference_change"] == "state_changed" or row["top_opportunity_reference_change"] == "state_changed":
        return "control_packet_snapshot_section"
    return "none"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramControlLoopSignalFeedV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramControlLoopSignalFeedV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_change_signal_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_loop_signal_feed_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_control_loop_signal_feed_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramControlLoopSignalFeedV1:
        change_row = _read_csv(self.change_signal_path)[0]
        loop_signal_mode = _loop_signal_mode(
            change_row["signal_priority"],
            change_row["interrupt_required_current"],
        )
        row = {
            "control_loop_signal_id": "internal_hot_news_program_control_loop_signal_latest",
            "loop_signal_mode": loop_signal_mode,
            "interrupt_required": change_row["interrupt_required_current"],
            "signal_priority": change_row["signal_priority"],
            "reopen_target": _reopen_target(change_row),
            "driver_signal_mode_current": change_row["program_driver_signal_mode_current"],
            "trading_day_state_current": change_row["trading_day_state_current"],
            "session_phase_current": change_row["session_phase_current"],
            "delivery_state": "program_control_loop_signal_feed_ready",
        }
        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_control_loop_signal_feed",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )
        summary = {
            "signal_row_count": 1,
            "loop_signal_mode": loop_signal_mode,
            "interrupt_required": row["interrupt_required"],
            "signal_priority": row["signal_priority"],
            "reopen_target": row["reopen_target"],
            "authoritative_output": "a_share_internal_hot_news_program_control_loop_signal_feed_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramControlLoopSignalFeedV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramControlLoopSignalFeedV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
