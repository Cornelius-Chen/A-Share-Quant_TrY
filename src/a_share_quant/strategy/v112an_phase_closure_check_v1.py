from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ANPhaseClosureCheckReport:
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


class V112ANPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ANPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112an_as_core_skeleton_pilot_result_review_success",
            "v112an_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112an_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112an_phase_check",
                "actual": {
                    "best_family_for_phase": phase_summary.get("best_family_for_phase"),
                    "best_family_for_role_state": phase_summary.get("best_family_for_role_state"),
                    "correction_bucket_count": phase_summary.get("correction_bucket_count"),
                },
                "reading": "The tiny pilot has now been translated into actionable mechanism hypotheses instead of raw score deltas alone.",
            }
        ]
        interpretation = [
            "V1.12AN closes once the tiny pilot can be explained in language and next-step pressure is narrowed.",
            "The next step must come from owner choice, not automatic expansion.",
        ]
        return V112ANPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112an_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ANPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
