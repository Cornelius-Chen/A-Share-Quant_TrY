from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RefreshTriggerMonitorReport:
    summary: dict[str, Any]
    trigger_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trigger_rows": self.trigger_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class RefreshTriggerMonitorAnalyzer:
    """Convert post-v2 refresh policy into explicit trigger flags."""

    def analyze(
        self,
        *,
        next_batch_refresh_readiness: dict[str, Any],
        v2_seed_continuation: dict[str, Any],
        q4_capture_acceptance: dict[str, Any],
        q3_drawdown_acceptance: dict[str, Any],
        specialist_payload: dict[str, Any],
    ) -> RefreshTriggerMonitorReport:
        readiness_summary = next_batch_refresh_readiness.get("summary", {})
        v2_seed_summary = v2_seed_continuation.get("summary", {})
        q4_summary = q4_capture_acceptance.get("summary", {})
        q3_summary = q3_drawdown_acceptance.get("summary", {})
        specialist_summary = specialist_payload.get("summary", {})

        archetype_gap_trigger = bool(
            readiness_summary.get("do_open_market_research_v2_refresh_now")
        )
        specialist_geography_trigger = bool(
            v2_seed_summary.get("do_continue_current_v2_seed_replay")
        )
        clean_frontier_trigger = not (
            q4_summary.get("do_continue_q4_capture_replay") is False
            and q3_summary.get("do_continue_q3_drawdown_replay") is False
        )
        secondary_status_break_trigger = not bool(
            readiness_summary.get("v2_seed_secondary_substrate_status")
        )

        active_trigger_count = sum(
            1
            for flag in (
                archetype_gap_trigger,
                specialist_geography_trigger,
                clean_frontier_trigger,
                secondary_status_break_trigger,
            )
            if flag
        )
        should_open_refresh = active_trigger_count > 0
        recommended_posture = (
            "open_refresh_design_cycle"
            if should_open_refresh
            else "maintain_waiting_state_until_new_trigger"
        )

        trigger_rows = [
            {
                "trigger_name": "new_archetype_gap_signal",
                "is_active": archetype_gap_trigger,
                "actual": {
                    "do_open_market_research_v2_refresh_now": readiness_summary.get(
                        "do_open_market_research_v2_refresh_now"
                    ),
                    "recommended_next_phase": readiness_summary.get("recommended_next_phase"),
                },
                "reading": "This trigger should only fire when the repo has an explicit post-v2 reason to open refresh design now.",
            },
            {
                "trigger_name": "materially_different_specialist_geography",
                "is_active": specialist_geography_trigger,
                "actual": {
                    "do_continue_current_v2_seed_replay": v2_seed_summary.get(
                        "do_continue_current_v2_seed_replay"
                    ),
                    "v2_seed_contributes_specialist_pockets": v2_seed_summary.get(
                        "v2_seed_contributes_specialist_pockets"
                    ),
                    "top_specialist_by_opportunity_count": specialist_summary.get(
                        "top_specialist_by_opportunity_count"
                    ),
                },
                "reading": "If v2-seed itself reopens locally, that would imply the suspect geography has changed enough to reconsider refresh timing.",
            },
            {
                "trigger_name": "clean_new_lane_frontier",
                "is_active": clean_frontier_trigger,
                "actual": {
                    "q4_closed": q4_summary.get("do_continue_q4_capture_replay") is False,
                    "q3_closed": q3_summary.get("do_continue_q3_drawdown_replay") is False,
                },
                "reading": "A refresh should stay closed while the currently opened lanes are still mixed and already slice-closed.",
            },
            {
                "trigger_name": "secondary_substrate_status_break",
                "is_active": secondary_status_break_trigger,
                "actual": {
                    "v2_seed_secondary_substrate_status": readiness_summary.get(
                        "v2_seed_secondary_substrate_status"
                    ),
                },
                "reading": "If v2-seed stops reading as a bounded secondary substrate, the repo may need a new refresh decision immediately.",
            },
        ]
        interpretation = [
            "This monitor is the operational version of the next-refresh policy.",
            "The repo should open a new refresh design cycle only when at least one trigger becomes active.",
            "If all trigger flags remain false, the correct posture is to keep waiting rather than inventing another batch by momentum.",
        ]
        summary = {
            "active_trigger_count": active_trigger_count,
            "archetype_gap_trigger": archetype_gap_trigger,
            "specialist_geography_trigger": specialist_geography_trigger,
            "clean_frontier_trigger": clean_frontier_trigger,
            "secondary_status_break_trigger": secondary_status_break_trigger,
            "should_open_refresh": should_open_refresh,
            "recommended_posture": recommended_posture,
        }
        return RefreshTriggerMonitorReport(
            summary=summary,
            trigger_rows=trigger_rows,
            interpretation=interpretation,
        )


def write_refresh_trigger_monitor_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: RefreshTriggerMonitorReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
