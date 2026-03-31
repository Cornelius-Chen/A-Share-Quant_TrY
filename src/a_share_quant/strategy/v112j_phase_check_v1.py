from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112JPhaseCheckReport:
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


class V112JPhaseCheckAnalyzer:
    def analyze(self, *, candidate_review_payload: dict[str, Any]) -> V112JPhaseCheckReport:
        review_summary = dict(candidate_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112j_as_candidate_structure_review_success",
            "formal_label_split_now": bool(review_summary.get("formal_label_split_now")),
            "bounded_follow_up_stage": str(review_summary.get("bounded_follow_up_stage", "")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "if_follow_up_is_opened_keep_it_bounded_to_high_level_consolidation_drafting_only",
        }
        evidence_rows = [
            {
                "evidence_name": "v112j_candidate_structure_review",
                "actual": {
                    "bucket_count_reviewed": int(review_summary.get("bucket_count_reviewed", 0)),
                    "bounded_follow_up_stage": review_summary.get("bounded_follow_up_stage"),
                },
                "reading": "V1.12J should identify whether any stage deserves bounded candidate-structure follow-up without forcing a formal label split.",
            }
        ]
        interpretation = [
            "V1.12J is a review judgment phase, not a relabeling phase.",
            "The review result narrows any future drafting to high_level_consolidation only.",
        ]
        return V112JPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112j_phase_check_report(*, reports_dir: Path, report_name: str, result: V112JPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
