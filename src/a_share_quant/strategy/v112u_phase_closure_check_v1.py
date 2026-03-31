from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112UPhaseClosureCheckReport:
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


class V112UPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112UPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112u_as_cpo_foundation_readiness_review_success",
            "v112u_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112u_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112u_phase_check",
                "actual": {
                    "foundation_is_complete_enough_for_bounded_research": phase_summary.get("foundation_is_complete_enough_for_bounded_research"),
                    "foundation_is_complete_enough_for_formal_training": phase_summary.get("foundation_is_complete_enough_for_formal_training"),
                    "remaining_material_gap_count": phase_summary.get("remaining_material_gap_count"),
                },
                "reading": "The CPO line now has an auditable readiness judgment: research yes, formal training not yet.",
            }
        ]
        interpretation = [
            "V1.12U closes once the CPO foundation has an explicit readiness judgment.",
            "The next lawful move is owner-level selection of the next research layer rather than automatic training.",
        ]
        return V112UPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112u_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112UPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
