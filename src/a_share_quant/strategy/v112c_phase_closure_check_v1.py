from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CPhaseClosureCheckReport:
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


class V112CPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112CPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112c_as_hotspot_review_and_sidecar_protocol_success",
            "v112c_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112c_waiting_state_now": True,
            "allow_auto_sidecar_run_now": False,
            "recommended_next_posture": "preserve_hotspot_map_and_sidecar_protocol_for_owner_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v112c_phase_check",
                "actual": {
                    "hotspot_review_present": bool(phase_summary.get("hotspot_review_present")),
                    "sidecar_protocol_present": bool(phase_summary.get("sidecar_protocol_present")),
                    "allow_sidecar_deployment_now": bool(phase_summary.get("allow_sidecar_deployment_now")),
                },
                "reading": "V1.12C closes once hotspot localization and the same-dataset sidecar protocol both exist, while deployment remains blocked.",
            }
        ]
        interpretation = [
            "V1.12C is a bounded planning-plus-execution phase, not a deployment phase.",
            "The correct close-out posture is waiting state until the owner decides whether to run the first black-box sidecar comparison.",
            "No automatic sidecar or strategy phase should be opened from here.",
        ]
        return V112CPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112c_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
