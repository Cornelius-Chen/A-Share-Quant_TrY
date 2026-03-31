from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113APhaseCharterReport:
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


class V113APhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113APhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        allowed_next_postures = {
            "initialize_bounded_theme_diffusion_state_schema_next",
            "open_bounded_theme_diffusion_state_schema_when_owner_continues",
        }
        if str(prior_summary.get("recommended_next_posture")) not in allowed_next_postures:
            raise ValueError("V1.13A requires V1.13 to recommend bounded theme-diffusion state-schema initialization.")

        summary = {
            "acceptance_posture": "open_v113a_theme_diffusion_state_schema_v1",
            "phase_name": "V1.13A Theme Diffusion State Schema",
            "ready_for_schema_freeze_next": True,
        }
        mission = {
            "goal": (
                "Freeze a first bounded state schema for A-share theme-diffusion carry, including state phases, stock roles, "
                "mainline strength dimensions, and context-backed driver slots."
            ),
            "why_now": (
                "V1.13 selected theme_diffusion_carry as the next higher-leverage line. The first lawful move is to define "
                "the state language before any modeling or execution work."
            ),
        }
        in_scope = [
            "theme-diffusion phase states",
            "stock-role taxonomy",
            "mainline strength dimensions",
            "context-backed driver dimensions",
            "open candidate-driver layer for later discovery",
            "review-only candidate-driver preservation",
        ]
        out_of_scope = [
            "execution timing schema",
            "intraday order-book or microstructure variables",
            "model training",
            "strategy integration",
            "formal driver scoring model",
        ]
        success_criteria = [
            "a usable schema exists for theme-diffusion state, role, and strength",
            "policy/industry/market/event drivers are explicitly recorded as separate dimensions",
            "the schema leaves room for subagent-discovered candidate drivers without freezing them prematurely",
        ]
        stop_criteria = [
            "the schema collapses into execution-level trigger design",
            "the schema tries to legislate candidate drivers as final variables without review",
        ]
        handoff_condition = (
            "mainline can review the first schema and then decide whether to add a bounded candidate-driver discovery layer"
        )
        return V113APhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113a_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V113APhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
