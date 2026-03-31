from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112APhaseCharterAnalyzer:
    """Open bounded pilot data assembly for the first cycle experiment."""

    def analyze(
        self,
        *,
        v112_phase_closure_payload: dict[str, Any],
        owner_phase_switch_approved: bool,
    ) -> V112APhaseCharterReport:
        closure_summary = dict(v112_phase_closure_payload.get("summary", {}))
        do_open_now = bool(closure_summary.get("enter_v112_waiting_state_now")) and owner_phase_switch_approved

        charter = {
            "mission": (
                "Assemble the first bounded pilot dataset draft for the frozen optical-link price-and-demand "
                "upcycle experiment, including object pool, initial role guesses, cycle window placeholders, "
                "and owner-correctable label fields."
            ),
            "in_scope": [
                "pilot object pool freeze",
                "initial object-role guesses",
                "cycle window placeholders",
                "owner-review label sheet",
                "explicit correction slots for missing objects and wrong labels",
            ],
            "out_of_scope": [
                "actual model fitting",
                "strategy integration",
                "intraday execution labels",
                "multi-cycle expansion",
                "black-box deployment",
            ],
            "success_criteria": [
                "produce a bounded object pool for the first pilot cycle",
                "produce a reviewable draft label sheet that the owner can correct",
                "leave no ambiguity about what still needs owner correction before training",
            ],
            "stop_criteria": [
                "if the object pool widens beyond the first pilot family",
                "if the sheet drifts into execution-level labeling",
                "if training starts before owner correction is possible",
            ],
            "handoff_condition": (
                "After bounded assembly, the next legal move is owner review and correction of the draft pilot "
                "dataset, not automatic training."
            ),
            "exploration_layer_phase": True,
            "owner_feedback_expected": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v112a_bounded_pilot_data_assembly"
                if do_open_now
                else "hold_v112a_until_owner_switch_after_v112_waiting_state"
            ),
            "do_open_v112a_now": do_open_now,
            "owner_phase_switch_approved": owner_phase_switch_approved,
            "recommended_first_action": "freeze_v112a_pilot_object_pool_v1",
        }
        interpretation = [
            "V1.12A exists so the owner can see and correct a real pilot dataset draft before any training begins.",
            "This phase is about assembling a usable first experiment sheet, not about fitting models.",
            "The next legal move is to freeze the first object pool and expose correction fields explicitly.",
        ]
        return V112APhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112a_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
