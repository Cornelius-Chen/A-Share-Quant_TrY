from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112DPhaseClosureCheckReport:
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


class V112DPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112DPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112d_as_same_dataset_sidecar_pilot_success",
            "v112d_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112d_waiting_state_now": True,
            "allow_auto_sidecar_deployment_now": False,
            "recommended_next_posture": "preserve_v112d_sidecar_results_for_owner_review_before_any_new_ml_branch",
        }
        evidence_rows = [
            {
                "evidence_name": "v112d_phase_check",
                "actual": {
                    "sidecar_pilot_present": bool(phase_summary.get("sidecar_pilot_present")),
                    "allow_sidecar_deployment_now": bool(phase_summary.get("allow_sidecar_deployment_now")),
                },
                "reading": "V1.12D closes once the first same-dataset sidecar comparison exists and deployment remains blocked.",
            }
        ]
        interpretation = [
            "V1.12D is a bounded comparison phase, not a deployment phase.",
            "The lawful next posture is waiting state until the owner reviews whether the sidecar improves decision value enough to continue.",
            "No automatic widening or model deployment is allowed from this result.",
        ]
        return V112DPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112d_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112DPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
