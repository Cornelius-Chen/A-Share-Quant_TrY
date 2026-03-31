from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112FPhaseClosureCheckReport:
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


class V112FPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112FPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112f_as_refinement_design_success",
            "v112f_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112f_waiting_state_now": True,
            "allow_auto_feature_mutation_now": False,
            "recommended_next_posture": "preserve_v112f_design_for_owner_review_before_any_dataset_or_model_change",
        }
        evidence_rows = [
            {
                "evidence_name": "v112f_phase_check",
                "actual": {
                    "refinement_design_present": bool(phase_summary.get("refinement_design_present")),
                    "primary_bottleneck_type": str(phase_summary.get("primary_bottleneck_type", "")),
                },
                "reading": "V1.12F closes once the next refinement basis is explicit and still blocked from automatic execution.",
            }
        ]
        interpretation = [
            "V1.12F is a bounded design phase, not a direct feature-mutation phase.",
            "The lawful next posture is waiting state until the owner accepts or edits the refinement basis.",
            "No automatic feature rewrite or retraining is allowed from this result alone.",
        ]
        return V112FPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112f_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112FPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
