from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AOPhaseCharterReport:
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


class V112AOPhaseCharterAnalyzer:
    def analyze(self, *, v112an_phase_closure_payload: dict[str, Any]) -> V112AOPhaseCharterReport:
        closure_summary = dict(v112an_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112an_success_criteria_met")):
            raise ValueError("V1.12AO requires the completed V1.12AN closure check.")

        charter = {
            "phase_name": "V1.12AO CPO Role-Layer Patch Pilot",
            "mission": (
                "Patch the weakest current layer, role-state separation, with a bounded set of market-observable "
                "microstructure and behavior features, then rerun the tiny core-skeleton pilot without widening scope."
            ),
            "in_scope": [
                "reuse the existing V1.12AM truth rows and time split",
                "add a small role-patch feature layer with no future leakage",
                "rerun guardrail and GBDT models",
                "compare role-state accuracy and confusion buckets before and after the patch",
            ],
            "out_of_scope": [
                "widening the pilot row set",
                "formal training promotion",
                "formal signal generation",
                "new generic audit layers",
            ],
            "success_criteria": [
                "the phase exposes whether role-state can be improved without widening geometry",
                "it explains which patch family contributes most to role separation",
                "it keeps the experiment report-only",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ao_cpo_role_layer_patch_pilot",
            "do_open_v112ao_now": True,
            "recommended_first_action": "freeze_v112ao_cpo_role_layer_patch_pilot_v1",
        }
        interpretation = [
            "V1.12AO exists to patch the current weakest layer before any pilot widening is considered.",
            "The right question is not whether more review is possible. The right question is whether role-state can improve with bounded non-leaking market-observable inputs.",
        ]
        return V112AOPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ao_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AOPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
