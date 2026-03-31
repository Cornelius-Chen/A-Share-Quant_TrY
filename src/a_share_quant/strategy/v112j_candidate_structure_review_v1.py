from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112JCandidateStructureReviewReport:
    summary: dict[str, Any]
    stage_review_rows: list[dict[str, Any]]
    bucket_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stage_review_rows": self.stage_review_rows,
            "bucket_review_rows": self.bucket_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112JCandidateStructureReviewAnalyzer:
    def analyze(
        self,
        *,
        protocol_payload: dict[str, Any],
        bucketization_payload: dict[str, Any],
    ) -> V112JCandidateStructureReviewReport:
        protocol_summary = dict(protocol_payload.get("summary", {}))
        bucket_summary = dict(bucketization_payload.get("summary", {}))
        if not bool(protocol_summary.get("protocol_ready_for_candidate_structure_review")):
            raise ValueError("V1.12J requires an active V1.12I review protocol.")
        if not bool(bucket_summary.get("ready_for_owner_review_next")):
            raise ValueError("V1.12J requires a completed reviewable bucketization output.")

        bucket_rows = list(bucketization_payload.get("bucket_rows", []))
        stage_to_rows: dict[str, list[dict[str, Any]]] = {}
        for row in bucket_rows:
            stage_to_rows.setdefault(str(row.get("bucket_stage")), []).append(row)

        bucket_review_rows: list[dict[str, Any]] = []
        for row in bucket_rows:
            sample_count = int(row.get("sample_count", 0))
            semantic = dict(row.get("mean_semantic_v2_features", {}))
            baseline_only = int(row.get("baseline_only_misread_count", 0))
            both_misread = int(row.get("both_models_misread_count", 0))
            bucket_name = str(row.get("bucket_name", ""))
            stage = str(row.get("bucket_stage", ""))

            if stage == "high_level_consolidation":
                if sample_count < 5:
                    disposition = "reject_for_formal_follow_up_sample_too_thin"
                    reading = "Semantically distinct, but too thin to justify bounded label follow-up."
                elif "breadth_thin_catalyst_stale" in bucket_name:
                    disposition = "needs_further_drafting_inside_bucket"
                    reading = "Large enough to matter, but still mixed; this is a drafting target, not a formal sublabel."
                elif baseline_only >= 10 and both_misread <= 2:
                    disposition = "strong_candidate_for_bounded_substate_drafting"
                    reading = "Distinct semantic profile and distinct error behavior; good candidate for a review-only substate draft."
                else:
                    disposition = "feature_side_only_for_now"
                    reading = "Useful organizing bucket, but not yet strong enough to justify further label action."
            else:
                if both_misread >= 30:
                    disposition = "feature_side_only_for_now"
                    reading = "Major-markup remains too mixed and too error-heavy for immediate label follow-up."
                else:
                    disposition = "organizing_bucket_only"
                    reading = "Useful for review structure, but not a current bounded label-refinement target."

            bucket_review_rows.append(
                {
                    "bucket_name": bucket_name,
                    "bucket_stage": stage,
                    "sample_count": sample_count,
                    "mean_semantic_v2_features": semantic,
                    "baseline_only_misread_count": baseline_only,
                    "both_models_misread_count": both_misread,
                    "review_disposition": disposition,
                    "reading": reading,
                }
            )

        stage_review_rows: list[dict[str, Any]] = []
        for stage, rows in stage_to_rows.items():
            dispositions = [r["review_disposition"] for r in bucket_review_rows if r["bucket_stage"] == stage]
            if stage == "high_level_consolidation":
                stage_review_rows.append(
                    {
                        "stage_name": stage,
                        "candidate_structure_present": True,
                        "formal_label_split_now": False,
                        "bounded_drafting_follow_up_worthwhile": True,
                        "reading": (
                            "This stage now shows distinct semantic/error buckets, but the current best posture is bounded drafting "
                            "follow-up rather than formal label splitting."
                        ),
                        "disposition_mix": dispositions,
                    }
                )
            else:
                stage_review_rows.append(
                    {
                        "stage_name": stage,
                        "candidate_structure_present": True,
                        "formal_label_split_now": False,
                        "bounded_drafting_follow_up_worthwhile": False,
                        "reading": (
                            "This stage has useful organizing buckets, but current error behavior remains too mixed for bounded "
                            "label-refinement follow-up."
                        ),
                        "disposition_mix": dispositions,
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112j_candidate_structure_review_v1",
            "bucket_count_reviewed": len(bucket_review_rows),
            "stage_count_reviewed": len(stage_review_rows),
            "formal_label_split_now": False,
            "bounded_follow_up_stage": "high_level_consolidation",
            "major_markup_follow_up_posture": "feature_side_only_for_now",
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The current bucketization output is strong enough to support candidate-structure review.",
            "Only high_level_consolidation clears the bar for bounded drafting follow-up; it still does not justify formal label splitting now.",
            "major_markup should remain on the feature side for now, because its buckets are still too mixed and error-heavy.",
        ]
        return V112JCandidateStructureReviewReport(
            summary=summary,
            stage_review_rows=stage_review_rows,
            bucket_review_rows=bucket_review_rows,
            interpretation=interpretation,
        )


def write_v112j_candidate_structure_review_report(
    *, reports_dir: Path, report_name: str, result: V112JCandidateStructureReviewReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
