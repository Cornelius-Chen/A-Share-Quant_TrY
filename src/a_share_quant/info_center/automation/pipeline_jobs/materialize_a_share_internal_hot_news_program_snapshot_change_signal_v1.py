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


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _change_state(*, id_changed: bool, score_delta: float) -> str:
    if id_changed:
        return "top_entity_changed"
    if abs(score_delta) >= 5.0:
        return "major_score_shift"
    if abs(score_delta) >= 1.0:
        return "minor_score_shift"
    return "stable"


def _state_change(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current != previous:
        return "state_changed"
    return "stable"


def _signal_priority(states: list[str]) -> str:
    if "state_changed" in states or "top_entity_changed" in states or "major_score_shift" in states:
        return "p0"
    return "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSnapshotChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSnapshotChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_snapshot_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_change_signal_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_snapshot_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSnapshotChangeSignalV1:
        current_rows = _read_csv(self.snapshot_path)
        current = current_rows[0]
        history_rows = _read_csv(self.history_path)
        previous = history_rows[0] if history_rows else None

        if previous is None:
            top_risk_change_state = "no_previous_baseline"
            top_opportunity_change_state = "no_previous_baseline"
            top_risk_changed = "false"
            top_opportunity_changed = "false"
            top_risk_score_delta = "0.0000"
            top_opportunity_score_delta = "0.0000"
            trading_day_state_change = "no_previous_baseline"
            session_phase_change = "no_previous_baseline"
            session_handling_mode_change = "no_previous_baseline"
        else:
            risk_id_changed = previous["top_risk_telegraph_id"] != current["top_risk_telegraph_id"]
            opportunity_id_changed = previous["top_opportunity_telegraph_id"] != current["top_opportunity_telegraph_id"]
            risk_score_delta = _to_float(current["top_risk_score"]) - _to_float(previous["top_risk_score"])
            opportunity_score_delta = _to_float(current["top_opportunity_score"]) - _to_float(
                previous["top_opportunity_score"]
            )
            top_risk_change_state = _change_state(id_changed=risk_id_changed, score_delta=risk_score_delta)
            top_opportunity_change_state = _change_state(
                id_changed=opportunity_id_changed,
                score_delta=opportunity_score_delta,
            )
            top_risk_changed = "true" if risk_id_changed else "false"
            top_opportunity_changed = "true" if opportunity_id_changed else "false"
            top_risk_score_delta = f"{risk_score_delta:.4f}"
            top_opportunity_score_delta = f"{opportunity_score_delta:.4f}"
            trading_day_state_change = _state_change(
                current["trading_day_state"],
                previous.get("trading_day_state") if previous else None,
            )
            session_phase_change = _state_change(
                current["session_phase"],
                previous.get("session_phase") if previous else None,
            )
            session_handling_mode_change = _state_change(
                current["session_handling_mode"],
                previous.get("session_handling_mode") if previous else None,
            )

        change_row = {
            "change_signal_id": "internal_hot_news_program_snapshot_change_latest",
            "top_risk_changed": top_risk_changed,
            "top_risk_change_state": top_risk_change_state,
            "top_risk_score_delta": top_risk_score_delta,
            "top_risk_current_telegraph_id": current["top_risk_telegraph_id"],
            "top_risk_current_score": current["top_risk_score"],
            "top_opportunity_changed": top_opportunity_changed,
            "top_opportunity_change_state": top_opportunity_change_state,
            "top_opportunity_score_delta": top_opportunity_score_delta,
            "top_opportunity_current_telegraph_id": current["top_opportunity_telegraph_id"],
            "top_opportunity_current_score": current["top_opportunity_score"],
            "trading_day_state_change": trading_day_state_change,
            "trading_day_state_current": current["trading_day_state"],
            "session_phase_change": session_phase_change,
            "session_phase_current": current["session_phase"],
            "session_handling_mode_change": session_handling_mode_change,
            "session_handling_mode_current": current["session_handling_mode"],
            "signal_priority": _signal_priority(
                [
                    top_risk_change_state,
                    top_opportunity_change_state,
                    trading_day_state_change,
                    session_phase_change,
                    session_handling_mode_change,
                ]
            ),
            "snapshot_state": current["snapshot_state"],
            "delivery_state": "snapshot_change_signal_ready",
        }

        self._write_csv(self.output_path, [change_row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.serving_path,
            [
                {
                    "view_id": "internal_hot_news_program_snapshot_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "change_row_count": 1,
            "top_risk_change_state": top_risk_change_state,
            "top_opportunity_change_state": top_opportunity_change_state,
            "top_risk_changed_flag": top_risk_changed,
            "top_opportunity_changed_flag": top_opportunity_changed,
            "trading_day_state_change": trading_day_state_change,
            "session_phase_change": session_phase_change,
            "session_handling_mode_change": session_handling_mode_change,
            "signal_priority": change_row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_snapshot_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSnapshotChangeSignalV1(summary=summary, rows=[change_row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSnapshotChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
