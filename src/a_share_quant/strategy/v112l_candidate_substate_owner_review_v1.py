from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112LCandidateSubstateOwnerReviewReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112LCandidateSubstateOwnerReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        candidate_substate_draft_payload: dict[str, Any],
    ) -> V112LCandidateSubstateOwnerReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        draft_summary = dict(candidate_substate_draft_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_owner_review_next")):
            raise ValueError("V1.12L requires an open owner-review charter.")
        if not bool(draft_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12L requires a completed V1.12K candidate-substate draft.")

        review_rows: list[dict[str, Any]] = []
        preserved_count = 0
        mixed_inner_target_count = 0

        for row in candidate_substate_draft_payload.get("candidate_substate_rows", []):
            candidate_name = str(row.get("candidate_substate_name", ""))
            readiness = str(row.get("drafting_readiness", ""))
            sample_count = int(row.get("sample_count", 0))
            label_distribution = dict(row.get("true_label_distribution", {}))
            failed_count = int(label_distribution.get("failed", 0))
            carry_count = int(label_distribution.get("carry_constructive", 0))

            if readiness == "ready_for_review_only_substate_draft" and sample_count >= 10:
                disposition = "preserve_as_review_only_candidate_substate"
                reading = (
                    "This candidate is coherent enough to preserve as a review-only substate draft, but not strong "
                    "enough to justify any formal label split."
                )
                preserved_count += 1
            elif readiness == "mixed_bucket_needs_inner_split_before_any_formal_follow_up":
                disposition = "preserve_only_as_inner_drafting_target"
                reading = (
                    "This mixed stall cluster should not be preserved as a clean candidate substate; it remains only "
                    "an optional future inner-drafting target."
                )
                mixed_inner_target_count += 1
            else:
                disposition = "drop_from_review_only_preservation"
                reading = "This draft row is too weak or too thin to preserve beyond the current review."

            review_rows.append(
                {
                    "candidate_substate_name": candidate_name,
                    "source_bucket_name": row.get("source_bucket_name"),
                    "sample_count": sample_count,
                    "drafting_readiness": readiness,
                    "carry_constructive_count": carry_count,
                    "failed_count": failed_count,
                    "review_disposition": disposition,
                    "reading": reading,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112l_candidate_substate_owner_review_v1",
            "reviewed_candidate_count": len(review_rows),
            "preserved_review_only_count": preserved_count,
            "mixed_inner_drafting_target_count": mixed_inner_target_count,
            "formal_label_split_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12L preserves only the review-only draft pieces that are already coherent enough to survive owner review.",
            "The mixed high-level stall cluster remains an optional inner-drafting target, not a preserved substate.",
            "No formal label split is authorized from this owner review.",
        ]
        return V112LCandidateSubstateOwnerReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v112l_candidate_substate_owner_review_report(
    *, reports_dir: Path, report_name: str, result: V112LCandidateSubstateOwnerReviewReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
