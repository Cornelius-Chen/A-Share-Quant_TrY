from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ADPhaseClosureCheckReport:
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


class V112ADPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ADPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ad_as_review_only_dynamic_role_transition_success",
            "v112ad_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ad_waiting_state_now": True,
            "allow_auto_feature_promotion_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ad_phase_check",
                "actual": {
                    "transition_event_count": phase_summary.get("transition_event_count"),
                    "dynamic_feature_count": phase_summary.get("dynamic_feature_count"),
                    "role_change_is_time_conditioned": phase_summary.get("role_change_is_time_conditioned"),
                },
                "reading": "Dynamic role migration is now a frozen review layer, but not yet a formal feature surface.",
            }
        ]
        interpretation = [
            "V1.12AD closes once dynamic role-transition reading is frozen as a bounded review layer.",
            "The next lawful move is owner review or bounded downstream feature-family design.",
        ]
        return V112ADPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ad_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ADPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
