from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113DPhaseCharterReport:
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


class V113DPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113DPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        if str(prior_summary.get("recommended_next_posture")) != "open_bounded_archetype_usage_pass_when_owner_continues":
            raise ValueError("V1.13D requires V1.13C to recommend a bounded archetype usage pass next.")

        summary = {
            "acceptance_posture": "open_v113d_bounded_archetype_usage_pass_v1",
            "phase_name": "V1.13D Bounded Archetype Usage Pass",
            "ready_for_archetype_usage_pass_next": True,
        }
        mission = {
            "goal": (
                "Apply the frozen theme-diffusion grammar to the three bounded seed archetypes and test whether state, role, "
                "strength, and driver layers remain interpretable without leaking into execution or feature promotion."
            ),
            "why_now": (
                "V1.13C established lawful schema-review-only usage for the four strongest drivers. The next bounded step is to "
                "see whether the grammar works cleanly at the archetype level."
            ),
        }
        in_scope = [
            "commercial_space_mainline",
            "stablecoin_theme_cycle",
            "low_altitude_economy_cycle",
            "review-only template usage judgments",
        ]
        out_of_scope = [
            "new archetype discovery",
            "feature candidacy",
            "model training",
            "execution implications",
            "strategy deployment",
        ]
        success_criteria = [
            "the grammar can be applied to the frozen archetypes without role/strength/driver collapse",
            "the review identifies which archetypes are clean review assets and which remain mixed or overextended",
        ]
        stop_criteria = [
            "the phase expands beyond the frozen archetype set",
            "the phase starts deriving execution or signal implications from the review",
        ]
        handoff_condition = "mainline can decide whether the theme-diffusion grammar is archetype-usable enough to support later bounded labeling or broader template work"
        return V113DPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113d_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V113DPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
