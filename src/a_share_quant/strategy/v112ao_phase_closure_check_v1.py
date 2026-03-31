from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AOPhaseClosureCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AOPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AOPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ao_as_role_layer_patch_pilot_success",
            "v112ao_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ao_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ao_phase_check",
                "actual": {
                    "role_state_accuracy_gain_after_patch": phase_summary.get("role_state_accuracy_gain_after_patch"),
                    "best_role_patch_family": phase_summary.get("best_role_patch_family"),
                },
                "reading": "The role patch pilot has now been reduced to a next-step decision instead of one more audit layer.",
            }
        ]
        interpretation = [
            "V1.12AO closes once the team knows whether role-state can be improved and what family drove that improvement.",
            "The next step must remain bounded and report-only.",
        ]
        return V112AOPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ao_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AOPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
