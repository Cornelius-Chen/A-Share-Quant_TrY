from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PPhaseClosureCheckReport:
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


class V112PPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112PPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112p_as_cpo_full_cycle_registry_success",
            "v112p_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "selected_archetype": phase_summary.get("selected_archetype"),
            "enter_v112p_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "discuss_missing_information_and_choose_bounded_candidate_validation_order",
        }
        evidence_rows = [
            {
                "evidence_name": "v112p_phase_check",
                "actual": {
                    "cohort_row_count": phase_summary.get("cohort_row_count"),
                    "source_count": phase_summary.get("source_count"),
                    "remaining_gap_count": phase_summary.get("remaining_gap_count"),
                },
                "reading": "The CPO line now has enough broad memory to move from object discovery to discussion about missing information and validation order.",
            }
        ]
        interpretation = [
            "V1.12P closes once the full-cycle registry is broad enough for owner review and gap discussion.",
            "This does not authorize automatic training or feature promotion.",
        ]
        return V112PPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112p_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
