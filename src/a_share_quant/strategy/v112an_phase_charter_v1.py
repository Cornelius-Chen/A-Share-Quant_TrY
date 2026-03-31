from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ANPhaseCharterReport:
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


class V112ANPhaseCharterAnalyzer:
    def analyze(self, *, v112am_phase_closure_payload: dict[str, Any]) -> V112ANPhaseCharterReport:
        closure_summary = dict(v112am_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112am_success_criteria_met")):
            raise ValueError("V1.12AN requires the completed V1.12AM closure check.")

        charter = {
            "phase_name": "V1.12AN CPO Core-Skeleton Pilot Result Review",
            "mission": (
                "Review why phase and catalyst-sequence labels were learned well, why role-state remains harder, "
                "and what the black-box model captured beyond the guardrail baseline."
            ),
            "in_scope": [
                "feature-family ablation for current pilot-local families",
                "role-state confusion review",
                "baseline-wrong / gbdt-right correction bucket review",
            ],
            "out_of_scope": [
                "new training expansion",
                "formal training promotion",
                "formal signal generation",
                "generic extra audit layers",
            ],
            "success_criteria": [
                "the phase explains current pilot behavior in language rather than just listing scores",
                "it identifies why role-state remains the harder layer",
                "it produces a concrete next-step bottleneck reading",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112an_cpo_core_skeleton_pilot_result_review",
            "do_open_v112an_now": True,
            "recommended_first_action": "freeze_v112an_cpo_core_skeleton_pilot_result_review_v1",
        }
        interpretation = [
            "V1.12AN is the explanation layer that turns the first tiny pilot into usable research knowledge.",
            "The goal is not another audit loop; the goal is to understand what the pilot learned and what it still failed to learn.",
        ]
        return V112ANPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112an_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ANPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
