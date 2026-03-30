from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PhaseStatusConsoleView:
    headline: str
    bullets: list[str]
    exit_code: int


class PhaseStatusConsoleFormatter:
    """Render the current phase status into a concise operator-facing console view."""

    def build_view(
        self,
        *,
        snapshot_payload: dict[str, Any],
        action_plan_payload: dict[str, Any],
    ) -> PhaseStatusConsoleView:
        snapshot_summary = dict(snapshot_payload.get("summary", {}))
        action_summary = dict(action_plan_payload.get("summary", {}))
        action_rows = list(action_plan_payload.get("action_rows", []))

        current_mode = str(snapshot_summary.get("current_mode", "unknown"))
        should_open_refresh = bool(snapshot_summary.get("should_open_refresh"))
        active_trigger_count = int(snapshot_summary.get("active_trigger_count", 0))
        all_gates_aligned = bool(snapshot_summary.get("all_gates_aligned", False))
        operator_posture = str(snapshot_summary.get("recommended_operator_posture", "unknown"))

        if should_open_refresh:
            headline = "PHASE STATUS: refresh trigger active"
            exit_code = 20
        elif current_mode == "explicit_no_trigger_wait" and all_gates_aligned:
            headline = "PHASE STATUS: explicit no-trigger wait"
            exit_code = 0
        else:
            headline = "PHASE STATUS: review required"
            exit_code = 10

        bullets = [
            f"mode: {current_mode}",
            f"active triggers: {active_trigger_count}",
            f"all gates aligned: {str(all_gates_aligned).lower()}",
            f"operator posture: {operator_posture}",
            f"action mode: {action_summary.get('action_mode', 'unknown')}",
        ]

        next_actions = []
        for row in action_rows[:3]:
            step = row.get("step")
            action_name = row.get("action_name")
            command = row.get("command")
            if command:
                next_actions.append(f"next {step}: {action_name} -> {command}")
            else:
                next_actions.append(f"next {step}: {action_name}")
        bullets.extend(next_actions)

        return PhaseStatusConsoleView(
            headline=headline,
            bullets=bullets,
            exit_code=exit_code,
        )
