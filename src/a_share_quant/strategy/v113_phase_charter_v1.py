from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113PhaseCharterReport:
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


class V113PhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113PhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        recommended_next_posture = str(prior_summary.get("recommended_next_posture", ""))
        if recommended_next_posture != "preserve_inner_draft_as_descriptive_review_asset_until_new evidence if no incremental gain":
            raise ValueError("V1.13 requires V1.12N to close with descriptive-only posture.")

        summary = {
            "acceptance_posture": "open_v113_theme_diffusion_carry_state_schema",
            "phase_name": "V1.13 Theme Diffusion Carry State Schema",
            "ready_for_template_entry_next": True,
        }
        mission = {
            "goal": (
                "Reallocate from the local high_level_consolidation refinement chain into a higher-leverage theme-diffusion "
                "carry template line for A-share mainline alpha."
            ),
            "why_now": (
                "V1.12M/N proved the current inner-refinement line creates descriptive review value but no predictive gain, "
                "so further pocket-deepening is no longer the best use of budget."
            ),
        }
        in_scope = [
            "freeze the shift away from V1.12 pocket refinement",
            "select theme_diffusion_carry as the next carry family focus",
            "define the first bounded template-entry basis for state-schema work",
        ]
        out_of_scope = [
            "live strategy integration",
            "execution timing logic",
            "feature promotion",
            "dataset-wide theme expansion",
            "model escalation",
        ]
        success_criteria = [
            "the new phase formally redirects effort from local refinement to a higher-leverage carry template line",
            "theme_diffusion_carry is selected with explicit bounded entry basis",
            "the phase remains schema-first rather than prematurely model-first",
        ]
        stop_criteria = [
            "the new phase drifts into execution-layer logic before the state schema exists",
            "the phase tries to reopen V1.12 local refinement as if it were still a predictive line",
        ]
        handoff_condition = "mainline can initialize a bounded theme-diffusion template entry artifact"
        return V113PhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113_phase_charter_report(*, reports_dir: Path, report_name: str, result: V113PhaseCharterReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
