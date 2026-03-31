from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113CPhaseClosureCheckReport:
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


class V113CPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113CPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113c_as_bounded_state_usage_review_success",
            "v113c_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113c_waiting_state_now": True,
            "allow_auto_model_open_now": False,
            "allow_auto_execution_schema_now": False,
            "allow_auto_driver_promotion_now": False,
            "recommended_next_posture": "open_bounded_archetype_usage_pass_when_owner_continues",
        }
        evidence_rows = [
            {
                "evidence_name": "v113c_phase_check",
                "actual": {
                    "reviewed_high_priority_driver_count": phase_summary.get("reviewed_high_priority_driver_count"),
                    "drivers_allowed_for_schema_review_only": phase_summary.get("drivers_allowed_for_schema_review_only"),
                },
                "reading": "V1.13C closes once the high-priority mainline drivers have lawful schema-review-only usage boundaries.",
            }
        ]
        interpretation = [
            "V1.13C remains a schema-governance phase, not a modeling or execution phase.",
            "The project may now move from driver review into bounded archetype usage without breaking mainline discipline.",
        ]
        return V113CPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113c_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113CPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
