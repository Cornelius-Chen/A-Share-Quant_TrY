from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PhaseStatusSnapshotReport:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class PhaseStatusSnapshotAnalyzer:
    """Compress current phase gates into one operator-facing status snapshot."""

    def analyze(
        self,
        *,
        v11_continuation: dict[str, Any],
        v2_seed_continuation: dict[str, Any],
        refresh_readiness: dict[str, Any],
        trigger_monitor: dict[str, Any],
        action_plan: dict[str, Any],
    ) -> PhaseStatusSnapshotReport:
        v11_summary = v11_continuation.get("summary", {})
        v2_summary = v2_seed_continuation.get("summary", {})
        refresh_summary = refresh_readiness.get("summary", {})
        trigger_summary = trigger_monitor.get("summary", {})
        action_summary = action_plan.get("summary", {})

        v11_paused = bool(
            v11_summary.get(
                "v11_current_loop_paused",
                (
                    v11_summary.get("do_continue_current_specialist_loop") is False
                    or v11_summary.get("all_market_v1_slices_closed", False)
                ),
            )
        )

        current_mode = (
            "explicit_no_trigger_wait"
            if not bool(trigger_summary.get("should_open_refresh"))
            else "refresh_triggered_preflight"
        )
        all_gates_aligned = (
            v11_paused
            and not bool(v2_summary.get("do_continue_current_v2_seed_replay"))
            and not bool(refresh_summary.get("do_open_market_research_v2_refresh_now"))
            and not bool(trigger_summary.get("should_open_refresh"))
            and str(action_summary.get("action_mode")) == "idle_wait_state"
        )

        status_rows = [
            {
                "layer_name": "v11_continuation",
                "current_state": "paused" if v11_paused else "open",
                "key_signal": v11_summary.get("recommended_next_phase"),
                "reading": "Primary specialist loop state.",
            },
            {
                "layer_name": "v2_seed_continuation",
                "current_state": "bounded" if not bool(v2_summary.get("do_continue_current_v2_seed_replay", False)) else "open",
                "key_signal": v2_summary.get("recommended_next_phase"),
                "reading": "Secondary substrate local replay state.",
            },
            {
                "layer_name": "refresh_readiness",
                "current_state": "closed" if not bool(refresh_summary.get("do_open_market_research_v2_refresh_now", False)) else "open",
                "key_signal": refresh_summary.get("recommended_next_phase"),
                "reading": "Whether the next refresh may open now.",
            },
            {
                "layer_name": "refresh_trigger_monitor",
                "current_state": "idle" if not bool(trigger_summary.get("should_open_refresh", False)) else "triggered",
                "key_signal": trigger_summary.get("recommended_posture"),
                "reading": "Whether any concrete trigger is active right now.",
            },
            {
                "layer_name": "operator_action_plan",
                "current_state": str(action_summary.get("action_mode")),
                "key_signal": action_summary.get("recommended_next_phase"),
                "reading": "What to do next under the current trigger state.",
            },
        ]
        summary = {
            "current_mode": current_mode,
            "all_gates_aligned": all_gates_aligned,
            "should_open_refresh": bool(trigger_summary.get("should_open_refresh")),
            "active_trigger_count": int(trigger_summary.get("active_trigger_count", 0)),
            "recommended_operator_posture": action_summary.get("action_mode"),
        }
        interpretation = [
            "This snapshot is the one-page read of the repo's current phase state.",
            "If all gates align and current_mode is explicit_no_trigger_wait, the repo should not invent new replay or refresh work.",
            "If later one of these layers changes, this snapshot should be regenerated before any new phase action.",
        ]
        return PhaseStatusSnapshotReport(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_phase_status_snapshot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: PhaseStatusSnapshotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
