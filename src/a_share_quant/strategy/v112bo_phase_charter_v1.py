from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BOPhaseCharterReport:
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


class V112BOPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bl_phase_closure_payload: dict[str, Any],
        v112bj_phase_closure_payload: dict[str, Any],
    ) -> V112BOPhaseCharterReport:
        if not bool(dict(v112bl_phase_closure_payload.get("summary", {})).get("v112bl_success_criteria_met")):
            raise ValueError("V1.12BO requires the completed V1.12BL closure check.")
        if not bool(dict(v112bj_phase_closure_payload.get("summary", {})).get("v112bj_success_criteria_met")):
            raise ValueError("V1.12BO requires the completed V1.12BJ closure check.")

        charter = {
            "phase_name": "V1.12BO CPO Internal Maturity Overlay Review",
            "mission": (
                "Freeze a lawful internal-maturity overlay family for CPO so later gate and fusion experiments "
                "can test congestion, role deterioration, internal breadth compression, and spillover saturation "
                "without replacing core role and phase truth."
            ),
            "in_scope": [
                "core-vs-branch-vs-spillover relative-strength overlays",
                "internal breadth compression and concentration overlays",
                "leader absorption fragility and role deterioration overlays",
                "branch promotion failure and spillover saturation overlays",
            ],
            "out_of_scope": [
                "formal training opening",
                "formal signal generation",
                "replacement of role-state truth",
            ],
            "success_criteria": [
                "the project has an explicit internal maturity overlay family",
                "the family is separated from core truth labels",
                "the family is ready to plug into later gate or selector-gate fusion experiments",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bo_cpo_internal_maturity_overlay_review",
            "do_open_v112bo_now": True,
            "recommended_first_action": "freeze_v112bo_cpo_internal_maturity_overlay_review_v1",
        }
        interpretation = [
            "V1.12BO exists because market-regime overlay alone did not reproduce the neutral selective edge.",
            "The next lawful layer is internal maturity, congestion, and role-quality deterioration inside the CPO cohort itself.",
        ]
        return V112BOPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bo_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BOPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
