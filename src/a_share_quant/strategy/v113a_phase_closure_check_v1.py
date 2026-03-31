from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113APhaseClosureCheckReport:
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


class V113APhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113APhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113a_as_theme_diffusion_state_schema_success",
            "v113a_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113a_waiting_state_now": True,
            "allow_auto_model_open_now": False,
            "allow_auto_execution_schema_now": False,
            "recommended_next_posture": "review_candidate_mainline_drivers_before_any_model_or_execution_line",
        }
        evidence_rows = [
            {
                "evidence_name": "v113a_phase_check",
                "actual": {
                    "phase_state_count": phase_summary.get("phase_state_count"),
                    "stock_role_count": phase_summary.get("stock_role_count"),
                    "strength_dimension_count": phase_summary.get("strength_dimension_count"),
                    "driver_dimension_count": phase_summary.get("driver_dimension_count"),
                },
                "reading": "V1.13A closes once the first bounded state schema is frozen cleanly and remains schema-first.",
            }
        ]
        interpretation = [
            "V1.13A is a successful schema phase, not a model or execution phase.",
            "Any next step should stay above the execution layer until driver review is clearer.",
        ]
        return V113APhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113a_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113APhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
