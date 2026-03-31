from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AAPhaseClosureCheckReport:
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


class V112AAPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AAPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112aa_as_bounded_cohort_map_success",
            "v112aa_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112aa_waiting_state_now": True,
            "allow_auto_labeling_now": False,
            "allow_auto_training_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112aa_phase_check",
                "actual": {
                    "object_row_count": phase_summary.get("object_row_count"),
                    "primary_core_truth_row_count": phase_summary.get("primary_core_truth_row_count"),
                    "pending_ambiguous_count": phase_summary.get("pending_ambiguous_count"),
                },
                "reading": "The bounded cohort map is now lawfully frozen and ready for owner consumption before any labeling move.",
            }
        ]
        interpretation = [
            "V1.12AA closes successfully once the cohort map boundary is frozen.",
            "The next lawful move is owner review or a bounded labeling review, not automatic training.",
        ]
        return V112AAPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aa_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AAPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
