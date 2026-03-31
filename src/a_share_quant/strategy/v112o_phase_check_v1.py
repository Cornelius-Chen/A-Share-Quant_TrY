from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112OPhaseCheckReport:
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


class V112OPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        study_scope_payload: dict[str, Any],
    ) -> V112OPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        scope_summary = dict(study_scope_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v112o_as_scope_freeze_only",
            "do_open_v112o_now": charter_summary.get("do_open_v112o_now"),
            "selected_archetype": charter_summary.get("selected_archetype"),
            "validated_local_seed_count": scope_summary.get("validated_local_seed_count"),
            "review_only_adjacent_candidate_count": scope_summary.get("review_only_adjacent_candidate_count"),
            "ready_for_phase_closure_next": True,
            "allow_auto_training_now": False,
            "allow_auto_dataset_widening_now": False,
            "recommended_next_posture": "close_v112o_and_decide_whether_to_open_bounded_adjacent_candidate_validation",
        }
        evidence_rows = [
            {
                "evidence_name": "study_scope",
                "actual": {
                    "validated_local_seed_count": scope_summary.get("validated_local_seed_count"),
                    "review_only_adjacent_candidate_count": scope_summary.get("review_only_adjacent_candidate_count"),
                    "bounded_study_dimension_count": scope_summary.get("bounded_study_dimension_count"),
                },
                "reading": "The optical-link line now distinguishes frozen training seeds from adjacent review-only cohort candidates.",
            }
        ]
        interpretation = [
            "V1.12O succeeds once CPO is frozen as a deep-study archetype without reopening the exhausted local refinement loop.",
            "This remains above automatic dataset widening and training.",
        ]
        return V112OPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112o_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112OPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
