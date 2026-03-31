from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113CPhaseCharterReport:
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


class V113CPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113CPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        if str(prior_summary.get("recommended_next_posture")) != "open_bounded_state_usage_review_on_high_priority_mainline_drivers_when_owner_continues":
            raise ValueError("V1.13C requires V1.13B to recommend bounded state-usage review on the high-priority drivers.")

        summary = {
            "acceptance_posture": "open_v113c_bounded_state_usage_review_v1",
            "phase_name": "V1.13C Bounded State Usage Review",
            "ready_for_state_usage_review_next": True,
        }
        mission = {
            "goal": (
                "Freeze how the four highest-priority mainline drivers may lawfully enter theme-diffusion state usage without "
                "being promoted into formal scoring variables or execution triggers."
            ),
            "why_now": (
                "V1.13B narrowed the candidate-driver set to a small high-priority quartet. The next bounded move is to define "
                "how they can be used in state review while keeping the project above model and execution layers."
            ),
        }
        in_scope = [
            "review usage posture for policy_backing_tier",
            "review usage posture for industrial_advantage_alignment",
            "review usage posture for market_regime_tailwind",
            "review usage posture for event_resonance_intensity",
            "freeze usage boundaries for schema review only",
        ]
        out_of_scope = [
            "formal driver promotion into model features",
            "driver scoring formulas",
            "execution trigger design",
            "strategy integration",
            "new candidate-driver discovery",
        ]
        success_criteria = [
            "the four highest-priority drivers receive bounded state-usage dispositions",
            "the project keeps driver usage in the schema-review layer rather than drifting into model or execution logic",
        ]
        stop_criteria = [
            "the phase tries to score or rank trades directly with the reviewed drivers",
            "the phase expands into lower-priority candidates instead of staying on the bounded quartet",
        ]
        handoff_condition = "mainline can decide whether to open a bounded archetype usage pass using only the reviewed driver quartet"
        return V113CPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113c_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V113CPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
