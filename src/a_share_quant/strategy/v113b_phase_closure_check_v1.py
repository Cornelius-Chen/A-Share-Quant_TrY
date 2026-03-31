from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113BPhaseClosureCheckReport:
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


class V113BPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113BPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113b_as_candidate_mainline_driver_review_success",
            "v113b_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113b_waiting_state_now": True,
            "allow_auto_model_open_now": False,
            "allow_auto_driver_promotion_now": False,
            "recommended_next_posture": "open_bounded_state_usage_review_on_high_priority_mainline_drivers_when_owner_continues",
        }
        evidence_rows = [
            {
                "evidence_name": "v113b_phase_check",
                "actual": {
                    "candidate_driver_count_reviewed": phase_summary.get("candidate_driver_count_reviewed"),
                    "bounded_state_usage_ready_count": phase_summary.get("bounded_state_usage_ready_count"),
                },
                "reading": "V1.13B closes once the review-only driver set is compressed into a bounded next-step review target.",
            }
        ]
        interpretation = [
            "V1.13B is a governance narrowing phase, not a model or deployment phase.",
            "The project now knows which candidate drivers deserve the next bounded schema attention.",
        ]
        return V113BPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113b_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113BPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
