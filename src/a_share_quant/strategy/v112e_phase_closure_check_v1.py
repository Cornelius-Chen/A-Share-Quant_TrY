from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112EPhaseClosureCheckReport:
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


class V112EPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112EPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112e_as_gbdt_attribution_review_success",
            "v112e_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112e_waiting_state_now": True,
            "allow_auto_model_escalation_now": False,
            "recommended_next_posture": "preserve_v112e_attribution_for_owner_review_before_any_new_ml_or_feature_phase",
        }
        evidence_rows = [
            {
                "evidence_name": "v112e_phase_check",
                "actual": {
                    "attribution_review_present": bool(phase_summary.get("attribution_review_present")),
                    "allow_model_deployment_now": bool(phase_summary.get("allow_model_deployment_now")),
                },
                "reading": "V1.12E closes once the first sidecar attribution explanation exists and deployment remains blocked.",
            }
        ]
        interpretation = [
            "V1.12E is a bounded explanation phase, not a new execution phase.",
            "The lawful next posture is waiting state until the owner reviews whether the attribution result changes the roadmap.",
            "No automatic escalation into new model families or deployment is allowed from this result.",
        ]
        return V112EPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112e_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112EPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
