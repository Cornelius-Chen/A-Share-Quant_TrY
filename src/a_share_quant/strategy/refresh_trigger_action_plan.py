from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RefreshTriggerActionPlanReport:
    summary: dict[str, Any]
    action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "action_rows": self.action_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class RefreshTriggerActionPlanAnalyzer:
    """Turn refresh-trigger state into an explicit operator checklist."""

    def analyze(
        self,
        *,
        monitor_payload: dict[str, Any],
        readiness_payload: dict[str, Any],
    ) -> RefreshTriggerActionPlanReport:
        monitor_summary = monitor_payload.get("summary", {})
        readiness_summary = readiness_payload.get("summary", {})

        should_open_refresh = bool(monitor_summary.get("should_open_refresh"))
        active_trigger_count = int(monitor_summary.get("active_trigger_count", 0))

        if should_open_refresh:
            action_mode = "triggered_refresh_preflight"
            action_rows = [
                {
                    "step": 1,
                    "action_name": "reconfirm_trigger_gate",
                    "command": "python scripts/run_next_batch_refresh_readiness.py --config config/next_batch_refresh_readiness_v1.yaml",
                    "purpose": "Reconfirm that refresh should really open before touching batch design.",
                },
                {
                    "step": 2,
                    "action_name": "regenerate_trigger_monitor",
                    "command": "python scripts/run_refresh_trigger_monitor.py --config config/refresh_trigger_monitor_v1.yaml",
                    "purpose": "Make sure at least one trigger is still active after recheck.",
                },
                {
                    "step": 3,
                    "action_name": "open_next_batch_design",
                    "command": "python scripts/run_next_suspect_batch_design.py --config config/next_suspect_batch_design_v1.yaml",
                    "purpose": "Recompute the missing-archetype design rule under the new trigger state.",
                },
                {
                    "step": 4,
                    "action_name": "audit_next_batch_manifest",
                    "command": "python scripts/run_next_suspect_batch_manifest.py --config config/market_research_v2_seed_manifest.yaml",
                    "purpose": "Validate the first concrete manifest before any new data bootstrap.",
                },
            ]
            interpretation = [
                "A trigger means the repo may reopen refresh work, not that it should skip straight to a new batch.",
                "The safest sequence is: reconfirm gate, rerun monitor, then reopen design and manifest audit.",
                "This keeps the next refresh trigger-driven instead of momentum-driven.",
            ]
        else:
            action_mode = "idle_wait_state"
            action_rows = [
                {
                    "step": 1,
                    "action_name": "keep_current_substrates_frozen",
                    "command": None,
                    "purpose": "Do not reopen local replay inside market_research_v1 or market_research_v2_seed.",
                },
                {
                    "step": 2,
                    "action_name": "rerun_refresh_monitor_on_new_signal",
                    "command": "python scripts/run_refresh_trigger_monitor.py --config config/refresh_trigger_monitor_v1.yaml",
                    "purpose": "Only rerun when a new suspect signal, new data refresh, or materially different geography appears.",
                },
                {
                    "step": 3,
                    "action_name": "reconfirm_refresh_gate_if_any_trigger_flips",
                    "command": "python scripts/run_next_batch_refresh_readiness.py --config config/next_batch_refresh_readiness_v1.yaml",
                    "purpose": "If any monitor flag turns true, recheck whether the repo should really open the next refresh cycle.",
                },
            ]
            interpretation = [
                "The current state is not just paused; it is an explicit no-trigger wait.",
                "No new batch design work should start until the monitor flips at least one trigger.",
                "This keeps the repo from reopening refresh work by habit.",
            ]

        summary = {
            "active_trigger_count": active_trigger_count,
            "should_open_refresh": should_open_refresh,
            "action_mode": action_mode,
            "recommended_next_phase": readiness_summary.get("recommended_next_phase"),
            "action_count": len(action_rows),
        }
        return RefreshTriggerActionPlanReport(
            summary=summary,
            action_rows=action_rows,
            interpretation=interpretation,
        )


def write_refresh_trigger_action_plan_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: RefreshTriggerActionPlanReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
