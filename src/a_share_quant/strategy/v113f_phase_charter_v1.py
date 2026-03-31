from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113FPhaseCharterReport:
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


class V113FPhaseCharterAnalyzer:
    """Open bounded pilot data assembly for the first theme-diffusion pilot."""

    def analyze(
        self,
        *,
        v113e_phase_closure_payload: dict[str, Any],
        owner_phase_switch_approved: bool,
    ) -> V113FPhaseCharterReport:
        closure_summary = dict(v113e_phase_closure_payload.get("summary", {}))
        do_open_now = bool(closure_summary.get("enter_v113e_waiting_state_now")) and owner_phase_switch_approved

        charter = {
            "mission": (
                "Assemble the first bounded pilot dataset draft for the frozen commercial_space_mainline "
                "theme-diffusion archetype, including a minimal object pool, initial role guesses, "
                "cycle window placeholders, and owner-correctable review fields."
            ),
            "in_scope": [
                "pilot object pool freeze for commercial_space_mainline",
                "initial role guesses using local sector-mapping evidence",
                "cycle window placeholders from local first-seen and last-seen evidence",
                "owner-review label sheet for state, role, strength, and driver flags",
                "explicit correction slots for missing objects, wrong roles, and wrong windows",
            ],
            "out_of_scope": [
                "model fitting",
                "signal generation",
                "execution implications",
                "automatic archetype expansion",
                "formal feature candidacy",
            ],
            "success_criteria": [
                "produce a bounded object pool for commercial_space_mainline using only local lawful evidence",
                "produce a reviewable label sheet that the owner can correct before any labeling freeze",
                "leave no ambiguity about which objects remain weak or noisy and therefore need owner review",
            ],
            "stop_criteria": [
                "if the pool widens beyond the selected commercial_space_mainline archetype",
                "if the assembly starts inferring execution or signal implications",
                "if training begins before the owner can correct the draft sheet",
            ],
            "handoff_condition": (
                "After bounded assembly, the next legal move is owner review of the pilot object pool and review sheet, "
                "not automatic labeling freeze or training."
            ),
            "exploration_layer_phase": False,
            "owner_feedback_expected": True,
        }
        summary = {
            "acceptance_posture": (
                "open_v113f_bounded_pilot_data_assembly"
                if do_open_now
                else "hold_v113f_until_owner_switch_after_v113e_waiting_state"
            ),
            "do_open_v113f_now": do_open_now,
            "owner_phase_switch_approved": owner_phase_switch_approved,
            "selected_archetype": "commercial_space_mainline",
            "recommended_first_action": "freeze_v113f_pilot_object_pool_v1",
        }
        interpretation = [
            "V1.13F exists to turn the first theme-diffusion pilot from a protocol into a concrete reviewable draft.",
            "This is still pre-label-freeze and pre-training; it only assembles the first lawful collaboration surface.",
            "The next legal move is to freeze a small object pool and expose owner correction fields explicitly.",
        ]
        return V113FPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v113f_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113FPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
