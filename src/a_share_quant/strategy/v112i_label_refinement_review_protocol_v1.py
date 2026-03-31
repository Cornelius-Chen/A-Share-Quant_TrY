from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ILabelRefinementReviewProtocolReport:
    summary: dict[str, Any]
    review_gate_rows: list[dict[str, Any]]
    rejection_gate_rows: list[dict[str, Any]]
    review_questions: list[str]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_gate_rows": self.review_gate_rows,
            "rejection_gate_rows": self.rejection_gate_rows,
            "review_questions": self.review_questions,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ILabelRefinementReviewProtocolAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        refinement_design_payload: dict[str, Any],
        semantic_rerun_payload: dict[str, Any],
    ) -> V112ILabelRefinementReviewProtocolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_protocol_next")):
            raise ValueError("V1.12I protocol requires an open V1.12I charter.")

        refinement_summary = dict(refinement_design_payload.get("summary", {}))
        rerun_summary = dict(semantic_rerun_payload.get("summary", {}))

        review_gate_rows = [
            {
                "gate_name": "candidate_substates_show_distinct_error_behavior",
                "required_reading": "different false-positive or false-negative profiles across candidate buckets",
                "why_it_matters": "A label split is not justified if all candidate groups fail in the same way.",
            },
            {
                "gate_name": "candidate_substates_show_distinct_semantic_v2_profiles",
                "required_reading": "freshness, persistence, or breadth-confirmation patterns differ materially across candidate buckets",
                "why_it_matters": "The split must reflect state meaning, not only arbitrary numerical separation.",
            },
            {
                "gate_name": "candidate_substates_reduce_review_confusion_without_fragmenting_sample_too_far",
                "required_reading": "review complexity falls while sample buckets remain usable for bounded follow-up",
                "why_it_matters": "The split should clarify the stage, not shatter it into tiny unstable shards.",
            },
        ]

        rejection_gate_rows = [
            {
                "gate_name": "no_distinct_semantic_profile",
                "reading": "Keep refinement on the feature side only if candidate buckets do not carry different semantic-v2 patterns.",
            },
            {
                "gate_name": "only_symbol_identity_changes",
                "reading": "Reject label-split candidacy if the buckets are merely symbol-specific rather than stage-specific.",
            },
            {
                "gate_name": "sample_fragmentation_exceeds_value",
                "reading": "Reject label-split candidacy if candidate buckets become too small to support bounded follow-up review.",
            },
        ]

        review_questions = [
            "Does high_level_consolidation contain at least one candidate substate with clearly different semantic-v2 meaning?",
            "Would a bounded split improve decision quality more than further feature refinement alone?",
            "Can the candidate split remain review-only first, without pretending to legislate a new formal label schema?",
        ]

        summary = {
            "acceptance_posture": "freeze_v112i_label_refinement_review_protocol_v1",
            "primary_bottleneck_type": str(refinement_summary.get("primary_bottleneck_type", "")),
            "semantic_rerun_acceptance_posture": str(rerun_summary.get("acceptance_posture", "")),
            "protocol_ready_for_candidate_structure_review": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "This protocol does not authorize a label split by itself.",
            "It defines the review threshold that candidate buckets must clear before label refinement becomes a lawful bounded follow-up.",
            "The current default remains feature-side refinement unless candidate structure shows distinct semantics plus distinct error behavior.",
        ]
        return V112ILabelRefinementReviewProtocolReport(
            summary=summary,
            review_gate_rows=review_gate_rows,
            rejection_gate_rows=rejection_gate_rows,
            review_questions=review_questions,
            interpretation=interpretation,
        )


def write_v112i_label_refinement_review_protocol_report(
    *, reports_dir: Path, report_name: str, result: V112ILabelRefinementReviewProtocolReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
