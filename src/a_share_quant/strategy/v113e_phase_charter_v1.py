from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113EPhaseCharterReport:
    summary: dict[str, Any]
    mission: dict[str, Any]
    in_scope: list[str]
    out_of_scope: list[str]
    success_criteria: list[str]
    stop_criteria: list[str]
    handoff_condition: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mission": self.mission,
            "in_scope": self.in_scope,
            "out_of_scope": self.out_of_scope,
            "success_criteria": self.success_criteria,
            "stop_criteria": self.stop_criteria,
            "handoff_condition": self.handoff_condition,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113EPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113EPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        if str(prior_summary.get("recommended_next_posture")) != "preserve_archetype_review_assets_and_wait_for_owner_direction":
            raise ValueError("V1.13E requires V1.13D to close cleanly before a downstream pilot is opened.")

        summary = {
            "acceptance_posture": "open_v113e_theme_diffusion_bounded_labeling_pilot_v1",
            "phase_name": "V1.13E Theme Diffusion Bounded Labeling Pilot",
            "ready_for_pilot_protocol_next": True,
        }
        mission = {
            "goal": (
                "Test whether the frozen theme-diffusion grammar is minimally trainable by freezing one bounded labeling and "
                "training-pilot protocol on the cleanest current archetype."
            ),
            "why_now": (
                "V1.13D shows the grammar is archetype-usable, with one clean core review asset. The next bounded question is "
                "whether that grammar can be turned into a small, disciplined labeling/training pilot without leaking into execution."
            ),
        }
        in_scope = [
            "select one clean archetype for the first bounded pilot",
            "freeze a minimal labeling schema for state, role, strength, and driver-presence review",
            "freeze a bounded report-only training posture",
        ]
        out_of_scope = [
            "execution timing",
            "signal generation",
            "strategy integration",
            "multi-archetype expansion",
            "heavy black-box deployment",
        ]
        success_criteria = [
            "one bounded theme-diffusion pilot archetype is selected",
            "a labeling/training protocol is frozen without execution leakage",
            "the next lawful move becomes bounded pilot data assembly rather than abstract debate",
        ]
        stop_criteria = [
            "the phase drifts into execution or signal logic",
            "the phase tries to generalize across multiple archetypes at once",
            "the labeling design cannot remain bounded and review-first",
        ]
        handoff_condition = "mainline can decide whether to assemble the first bounded pilot dataset for the selected archetype"
        return V113EPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113e_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V113EPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
