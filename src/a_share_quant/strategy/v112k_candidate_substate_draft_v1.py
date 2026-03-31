from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112KCandidateSubstateDraftReport:
    summary: dict[str, Any]
    candidate_substate_rows: list[dict[str, Any]]
    excluded_bucket_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_substate_rows": self.candidate_substate_rows,
            "excluded_bucket_rows": self.excluded_bucket_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112KCandidateSubstateDraftAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        candidate_review_payload: dict[str, Any],
        bucketization_payload: dict[str, Any],
    ) -> V112KCandidateSubstateDraftReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(candidate_review_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_drafting_next")):
            raise ValueError("V1.12K requires an open V1.12K charter.")
        if str(review_summary.get("bounded_follow_up_stage")) != "high_level_consolidation":
            raise ValueError("V1.12K requires high_level_consolidation as the bounded follow-up stage.")

        review_rows = list(candidate_review_payload.get("bucket_review_rows", []))
        bucket_rows = {str(r.get("bucket_name")): r for r in bucketization_payload.get("bucket_rows", [])}

        candidate_substate_rows: list[dict[str, Any]] = []
        excluded_bucket_rows: list[dict[str, Any]] = []

        for review_row in review_rows:
            if str(review_row.get("bucket_stage")) != "high_level_consolidation":
                continue
            bucket_name = str(review_row.get("bucket_name", ""))
            disposition = str(review_row.get("review_disposition", ""))
            source_bucket = bucket_rows[bucket_name]
            sample_count = int(review_row.get("sample_count", 0))
            semantics = dict(review_row.get("mean_semantic_v2_features", {}))

            if disposition == "strong_candidate_for_bounded_substate_drafting":
                if "breadth_rich_catalyst_active" in bucket_name:
                    candidate_name = "candidate_high_level_base_with_breadth_confirmation"
                    reading = (
                        "A review-only draft for high-level bases that still show strong breadth confirmation plus "
                        "cross-day catalyst support, even though many samples still fail."
                    )
                else:
                    candidate_name = "candidate_high_level_base_with_thin_breadth_transition"
                    reading = (
                        "A review-only draft for high-level bases where catalyst persistence remains but breadth is thin, "
                        "suggesting a transition pocket rather than a clean continuation."
                    )
                candidate_substate_rows.append(
                    {
                        "candidate_substate_name": candidate_name,
                        "source_bucket_name": bucket_name,
                        "sample_count": sample_count,
                        "drafting_readiness": "ready_for_review_only_substate_draft",
                        "mean_semantic_v2_features": semantics,
                        "true_label_distribution": source_bucket.get("true_label_distribution", {}),
                        "error_pattern_distribution": source_bucket.get("error_pattern_distribution", {}),
                        "reading": reading,
                        "representative_rows": source_bucket.get("representative_rows", [])[:3],
                    }
                )
            elif disposition == "needs_further_drafting_inside_bucket":
                candidate_substate_rows.append(
                    {
                        "candidate_substate_name": "candidate_mixed_high_level_stall_cluster",
                        "source_bucket_name": bucket_name,
                        "sample_count": sample_count,
                        "drafting_readiness": "mixed_bucket_needs_inner_split_before_any_formal_follow_up",
                        "mean_semantic_v2_features": semantics,
                        "true_label_distribution": source_bucket.get("true_label_distribution", {}),
                        "error_pattern_distribution": source_bucket.get("error_pattern_distribution", {}),
                        "reading": (
                            "This is the largest mixed high-level consolidation bucket. It is worth review-only inner drafting, "
                            "but too mixed to become a direct candidate substate."
                        ),
                        "representative_rows": source_bucket.get("representative_rows", [])[:3],
                    }
                )
            else:
                excluded_bucket_rows.append(
                    {
                        "source_bucket_name": bucket_name,
                        "review_disposition": disposition,
                        "sample_count": sample_count,
                        "reading": str(review_row.get("reading", "")),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112k_candidate_substate_draft_v1",
            "candidate_substate_count": len(candidate_substate_rows),
            "excluded_bucket_count": len(excluded_bucket_rows),
            "formal_label_split_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12K produces a review-only candidate-substate draft for high_level_consolidation.",
            "Two candidate substates are directly draftable now, while one large mixed bucket remains only an inner-drafting target.",
            "No formal label split is authorized from this draft alone.",
        ]
        return V112KCandidateSubstateDraftReport(
            summary=summary,
            candidate_substate_rows=candidate_substate_rows,
            excluded_bucket_rows=excluded_bucket_rows,
            interpretation=interpretation,
        )


def write_v112k_candidate_substate_draft_report(
    *, reports_dir: Path, report_name: str, result: V112KCandidateSubstateDraftReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
