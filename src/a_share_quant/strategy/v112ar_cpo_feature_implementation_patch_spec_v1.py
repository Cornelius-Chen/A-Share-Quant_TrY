from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ARCPOFeatureImplementationPatchSpecReport:
    summary: dict[str, Any]
    board_patch_rule_rows: list[dict[str, Any]]
    calendar_patch_rule_rows: list[dict[str, Any]]
    patch_usage_boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "board_patch_rule_rows": self.board_patch_rule_rows,
            "calendar_patch_rule_rows": self.calendar_patch_rule_rows,
            "patch_usage_boundary_rows": self.patch_usage_boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ARCPOFeatureImplementationPatchSpecAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        patch_review_payload: dict[str, Any],
    ) -> V112ARCPOFeatureImplementationPatchSpecReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ar_now")):
            raise ValueError("V1.12AR must be open before the patch spec freeze runs.")

        review_summary = dict(patch_review_payload.get("summary", {}))
        if not bool(review_summary.get("should_patch_feature_implementation_before_row_widen")):
            raise ValueError("V1.12AR expects V1.12AQ to require an implementation patch before row widen.")

        board_patch_rule_rows = [
            {
                "rule_name": "board_vendor_selection_rule",
                "rule_scope": "daily_board_series",
                "frozen_rule": (
                    "Use bounded cohort-reconstructed daily board proxy as primary source. "
                    "Use explicit concept-index overlay only as secondary reference, not as canonical replacement."
                ),
                "point_in_time_guard": "same-day observable cohort and board inputs only",
                "audit_posture": "store vendor_source_class and fallback_reason per row",
            },
            {
                "rule_name": "breadth_formula_rule",
                "rule_scope": "daily_board_series",
                "frozen_rule": (
                    "Compute cohort_breadth_daily as weighted same-day participation ratio: "
                    "core truth rows weight 1.00, validated adjacent/support rows 0.75, branch rows 0.50, "
                    "spillover/memory rows 0.25."
                ),
                "point_in_time_guard": "use same-day status only; no future-stage reassignment",
                "audit_posture": "store contributing bucket counts and weighted numerator/denominator",
            },
            {
                "rule_name": "turnover_normalization_rule",
                "rule_scope": "daily_board_series",
                "frozen_rule": (
                    "Normalize turnover_pressure_daily with trailing 20-day rolling percentile on the bounded board proxy, "
                    "then map to {calm, normal, elevated, exhausted} state."
                ),
                "point_in_time_guard": "trailing window only; no centered or forward normalization",
                "audit_posture": "store raw proxy, rolling window length, percentile, and mapped state",
            },
        ]

        calendar_patch_rule_rows = [
            {
                "rule_name": "expected_window_fill_rule",
                "rule_scope": "future_catalyst_calendar",
                "frozen_rule": (
                    "Fill annual-event windows from official disclosed dates when present; otherwise use prior-cycle month/day "
                    "bucket with explicit review flag. Fill quarterly anchors from official results windows or quarter-month "
                    "cadence with explicit uncertainty flag."
                ),
                "point_in_time_guard": "never infer exact dates when only cadence is known",
                "audit_posture": "store disclosed_vs_inferred flag and window_uncertainty_state",
            },
            {
                "rule_name": "confidence_tier_mapping_rule",
                "rule_scope": "future_catalyst_calendar",
                "frozen_rule": (
                    "Map source confidence as Tier1 official event/IR calendar, Tier2 official company PR/news release, "
                    "Tier3 official results schedule/prepared remarks cadence, Tier4 manual placeholder with explicit missingness."
                ),
                "point_in_time_guard": "confidence may degrade but cannot be silently upgraded after the fact",
                "audit_posture": "store original source class and confidence_tier at record creation",
            },
            {
                "rule_name": "calendar_rollforward_rule",
                "rule_scope": "future_catalyst_calendar",
                "frozen_rule": (
                    "Archive expired anchors, create next-cycle placeholders only for cadence buckets with prior-cycle confirmation, "
                    "and keep unresolved placeholders pending rather than silently rolling them forward."
                ),
                "point_in_time_guard": "no future-cycle anchor may be created from hindsight-only knowledge",
                "audit_posture": "store prior_anchor_reference and rollforward_reason",
            },
        ]

        patch_usage_boundary_rows = [
            {
                "boundary_name": "board_condition_usage_boundary",
                "current_right": "guarded_auxiliary_only",
                "upgrade_condition": "all 3 board patch rules frozen and backfilled on current truth rows",
            },
            {
                "boundary_name": "catalyst_sequence_usage_boundary",
                "current_right": "core_label_with_partial_calendar_support",
                "upgrade_condition": "all 3 calendar patch rules frozen and backfilled on current truth rows",
            },
            {
                "boundary_name": "row_geometry_widen_boundary",
                "current_right": "blocked",
                "upgrade_condition": "board and calendar patch backfill completed on the current 7 truth rows first",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112ar_cpo_feature_implementation_patch_spec_v1",
            "board_patch_rule_count": len(board_patch_rule_rows),
            "calendar_patch_rule_count": len(calendar_patch_rule_rows),
            "total_patch_rule_count": len(board_patch_rule_rows) + len(calendar_patch_rule_rows),
            "next_lawful_move": "bounded_implementation_backfill_on_current_truth_rows",
            "allow_row_geometry_widen_now": False,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12AR freezes the minimum bounded implementation rule set instead of pretending the operational gaps are harmless.",
            "The project should now patch implementation on the current 7 truth rows before any row-geometry widen.",
        ]
        return V112ARCPOFeatureImplementationPatchSpecReport(
            summary=summary,
            board_patch_rule_rows=board_patch_rule_rows,
            calendar_patch_rule_rows=calendar_patch_rule_rows,
            patch_usage_boundary_rows=patch_usage_boundary_rows,
            interpretation=interpretation,
        )


def write_v112ar_cpo_feature_implementation_patch_spec_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ARCPOFeatureImplementationPatchSpecReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
