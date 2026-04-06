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


def _action_change_state(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current != previous:
        return "action_changed"
    return "stable"


def _global_signal_priority(
    *,
    global_mode_state: str,
    top_risk_action_state: str,
    top_opportunity_action_state: str,
    session_action_gate_state: str,
    session_phase_state: str,
) -> str:
    if "action_changed" in {global_mode_state, top_risk_action_state, top_opportunity_action_state, session_action_gate_state}:
        return "p0"
    if "state_changed" in {session_phase_state}:
        return "p0"
    return "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramChangeActionSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramChangeActionSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.action_surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_change_action_surface_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_change_action_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_change_action_signal_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_change_action_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramChangeActionSignalV1:
        current = _read_csv(self.action_surface_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        top_risk_action_state = _action_change_state(
            current["top_risk_action"],
            previous["top_risk_action"] if previous else None,
        )
        top_opportunity_action_state = _action_change_state(
            current["top_opportunity_action"],
            previous["top_opportunity_action"] if previous else None,
        )
        global_mode_state = _action_change_state(
            current["global_program_action_mode"],
            previous["global_program_action_mode"] if previous else None,
        )
        session_action_gate_state = _action_change_state(
            current["session_action_gate"],
            previous.get("session_action_gate") if previous else None,
        )
        session_phase_state = _action_change_state(
            current["session_phase"],
            previous.get("session_phase") if previous else None,
        )

        row = {
            "change_action_signal_id": "internal_hot_news_program_change_action_signal_latest",
            "top_risk_action_state": top_risk_action_state,
            "top_risk_action_current": current["top_risk_action"],
            "top_opportunity_action_state": top_opportunity_action_state,
            "top_opportunity_action_current": current["top_opportunity_action"],
            "global_program_action_mode_state": global_mode_state,
            "global_program_action_mode_current": current["global_program_action_mode"],
            "session_phase_state": session_phase_state,
            "session_phase_current": current["session_phase"],
            "session_action_gate_state": session_action_gate_state,
            "session_action_gate_current": current["session_action_gate"],
            "signal_priority": _global_signal_priority(
                global_mode_state=global_mode_state,
                top_risk_action_state=top_risk_action_state,
                top_opportunity_action_state=top_opportunity_action_state,
                session_action_gate_state=session_action_gate_state,
                session_phase_state=session_phase_state,
            ),
            "delivery_state": "program_change_action_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.serving_path,
            [
                {
                    "view_id": "internal_hot_news_program_change_action_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "top_risk_action_state": top_risk_action_state,
            "top_opportunity_action_state": top_opportunity_action_state,
            "global_program_action_mode_state": global_mode_state,
            "session_phase_state": session_phase_state,
            "session_action_gate_state": session_action_gate_state,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_change_action_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramChangeActionSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramChangeActionSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
