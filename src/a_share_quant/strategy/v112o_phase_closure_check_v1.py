from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112OPhaseClosureCheckReport:
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


class V112OPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112OPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112o_as_optical_link_deep_scope_success",
            "v112o_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "selected_archetype": phase_summary.get("selected_archetype"),
            "enter_v112o_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_dataset_widening_now": False,
            "recommended_next_posture": "decide_between_bounded_adjacent_candidate_validation_and_bounded_cohort_widening_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v112o_phase_check",
                "actual": {
                    "validated_local_seed_count": phase_summary.get("validated_local_seed_count"),
                    "review_only_adjacent_candidate_count": phase_summary.get("review_only_adjacent_candidate_count"),
                },
                "reading": "The optical-link line now preserves both clean seeds and adjacent review-only expansion candidates inside one lawful scope.",
            }
        ]
        interpretation = [
            "V1.12O closes once CPO is frozen as a deep-study archetype rather than only a narrow pilot dataset.",
            "The line remains above downstream cohort widening and training until a later bounded validation move is chosen.",
        ]
        return V112OPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112o_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112OPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
