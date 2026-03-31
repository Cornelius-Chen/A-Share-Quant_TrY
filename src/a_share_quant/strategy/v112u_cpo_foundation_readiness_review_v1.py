from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112UCPOFoundationReadinessReviewReport:
    summary: dict[str, Any]
    readiness_rows: list[dict[str, Any]]
    remaining_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "readiness_rows": self.readiness_rows,
            "remaining_gap_rows": self.remaining_gap_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112UCPOFoundationReadinessReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        schema_payload: dict[str, Any],
        adjacent_payload: dict[str, Any],
        chronology_payload: dict[str, Any],
        spillover_payload: dict[str, Any],
    ) -> V112UCPOFoundationReadinessReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112u_now")):
            raise ValueError("V1.12U must be open before the readiness review runs.")

        schema_summary = dict(schema_payload.get("summary", {}))
        adjacent_summary = dict(adjacent_payload.get("summary", {}))
        chronology_summary = dict(chronology_payload.get("summary", {}))
        spillover_summary = dict(spillover_payload.get("summary", {}))

        readiness_rows = [
            {
                "dimension": "registry_schema_hardening",
                "status": "sufficient_for_bounded_research",
                "actual": {
                    "cycle_stage_count": schema_summary.get("cycle_stage_count"),
                    "information_layer_count": schema_summary.get("information_layer_count"),
                    "bucket_count": schema_summary.get("bucket_count"),
                    "feature_slot_count": schema_summary.get("feature_slot_count"),
                },
                "reading": "The information registry now has enough structure to support deep review and cycle reconstruction without flattening layers.",
            },
            {
                "dimension": "adjacent_cohort_cleanliness",
                "status": "partially_clean_but_research_usable",
                "actual": {
                    "validated_review_asset_count": adjacent_summary.get("validated_review_asset_count"),
                    "pending_split_or_role_validation_count": adjacent_summary.get("pending_split_or_role_validation_count"),
                },
                "reading": "The adjacent pool is no longer flat; several rows are preserved cleanly while unresolved rows remain explicit pending assets.",
            },
            {
                "dimension": "chronology_structure",
                "status": "sufficient_for_bounded_research",
                "actual": {
                    "chronology_segment_count": chronology_summary.get("chronology_segment_count"),
                    "timing_gap_count": chronology_summary.get("timing_gap_count"),
                    "normalized_calendar_anchor_count": chronology_summary.get("normalized_calendar_anchor_count"),
                },
                "reading": "The chronology layer now distinguishes event, lag, and quiet windows well enough for bounded cycle reconstruction.",
            },
            {
                "dimension": "spillover_noise_preservation",
                "status": "research_usable_but_not_training_usable",
                "actual": {
                    "candidate_a_share_spillover_factor_count": spillover_summary.get("candidate_a_share_spillover_factor_count"),
                    "pure_name_bonus_or_board_follow_count": spillover_summary.get("pure_name_bonus_or_board_follow_count"),
                },
                "reading": "Mixed-relevance rows are preserved with explicit buckets, which is useful for review and later factor discovery but not for immediate training.",
            },
        ]

        remaining_gap_rows = [
            {
                "gap_name": "unresolved_adjacent_role_split",
                "why_it_still_matters": "Several adjacent rows remain structurally mixed, which weakens direct training use even though research review can proceed.",
                "current_scope": "603083 / 688205 / 301205 / 300620 / 300548 / 300757 / 000988 / 688498 / 688313",
            },
            {
                "gap_name": "daily_board_level_chronology_series_missing",
                "why_it_still_matters": "Chronology grammar exists, but daily concept-index, breadth, and turnover sequences are not yet normalized into a full day-by-day table.",
                "current_scope": "index_sentiment_and_liquidity layer",
            },
            {
                "gap_name": "future_catalyst_calendar_not_yet_standardized_into_operational_table",
                "why_it_still_matters": "Public catalyst anchors exist, but the forward calendar is not yet converted into a research-usable recurring table.",
                "current_scope": "message_and_catalyst plus earnings timing surface",
            },
            {
                "gap_name": "spillover_rows_not_yet_factor-tested",
                "why_it_still_matters": "The noisy rows are preserved, but they have not yet been tested as A-share-specific spillover factors or excluded from that path.",
                "current_scope": "mixed-relevance spillover review layer",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112u_cpo_foundation_readiness_review_v1",
            "foundation_is_normed_for_research": True,
            "foundation_is_complete_enough_for_bounded_research": True,
            "foundation_is_complete_enough_for_formal_training": False,
            "remaining_material_gap_count": len(remaining_gap_rows),
            "recommended_next_posture": "owner_review_then_bounded_cycle_reconstruction_or_cohort_map",
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The CPO information foundation has crossed the threshold for bounded deep research.",
            "It has not crossed the threshold for formal training because several material gaps remain unresolved.",
            "The correct next move is an owner-level decision on the next research layer, not automatic training or feature promotion.",
        ]
        return V112UCPOFoundationReadinessReviewReport(
            summary=summary,
            readiness_rows=readiness_rows,
            remaining_gap_rows=remaining_gap_rows,
            interpretation=interpretation,
        )


def write_v112u_cpo_foundation_readiness_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112UCPOFoundationReadinessReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
