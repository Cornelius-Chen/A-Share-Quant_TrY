from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ALCPOBoundedTrainingReadinessReviewReport:
    summary: dict[str, Any]
    layer_readiness_rows: list[dict[str, Any]]
    core_trainable_set_rows: list[dict[str, Any]]
    guarded_trainable_set_rows: list[dict[str, Any]]
    not_yet_trainable_rows: list[dict[str, Any]]
    bottleneck_attribution_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "layer_readiness_rows": self.layer_readiness_rows,
            "core_trainable_set_rows": self.core_trainable_set_rows,
            "guarded_trainable_set_rows": self.guarded_trainable_set_rows,
            "not_yet_trainable_rows": self.not_yet_trainable_rows,
            "bottleneck_attribution_rows": self.bottleneck_attribution_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ALCPOBoundedTrainingReadinessReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        feature_binding_payload: dict[str, Any],
        feature_family_payload: dict[str, Any],
        daily_board_payload: dict[str, Any],
        future_calendar_payload: dict[str, Any],
    ) -> V112ALCPOBoundedTrainingReadinessReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112al_now")):
            raise ValueError("V1.12AL must be open before the readiness review runs.")

        dataset_summary = dict(dataset_assembly_payload.get("summary", {}))
        binding_summary = dict(feature_binding_payload.get("summary", {}))
        feature_summary = dict(feature_family_payload.get("summary", {}))
        daily_gap_rows = list(daily_board_payload.get("unresolved_gap_rows", []))
        calendar_gap_rows = list(future_calendar_payload.get("unresolved_gap_rows", []))

        dataset_rows = list(dataset_assembly_payload.get("dataset_draft_rows", []))
        truth_rows = [row for row in dataset_rows if bool(row.get("include_in_truth_candidate_rows"))]
        if len(truth_rows) != int(dataset_summary.get("truth_candidate_row_count", 0)):
            raise ValueError("Truth-row count mismatch in V1.12AL inputs.")

        binding_rows = list(feature_binding_payload.get("binding_rows", []))
        binding_index: dict[tuple[str, str], dict[str, Any]] = {
            (str(row.get("symbol")), str(row.get("label_name"))): row for row in binding_rows
        }
        if not binding_index:
            raise ValueError("V1.12AL requires row-level binding rows from V1.12AK.")

        core_labels = sorted(
            {
                str(label)
                for row in truth_rows
                for label in list(row.get("allowed_ready_labels", []))
            }
        )
        guarded_labels = sorted(
            {
                str(label)
                for row in truth_rows
                for label in list(row.get("allowed_guarded_labels", []))
            }
        )

        truth_stage_windows = sorted(
            {
                str(window)
                for row in truth_rows
                for window in list(row.get("active_stage_windows", []))
            }
        )
        has_quiet_window_truth = any("quiet_window" in window for window in truth_stage_windows)
        has_spillover_truth = any(str(row.get("cohort_layer")) == "spillover_candidate" for row in truth_rows)

        core_trainable_set_rows: list[dict[str, Any]] = []
        for row in truth_rows:
            symbol = str(row.get("symbol"))
            row_bindings = [
                entry for (entry_symbol, _), entry in binding_index.items() if entry_symbol == symbol
            ]
            direct_bindable_count = sum(
                1 for entry in row_bindings if str(entry.get("binding_posture")) == "direct_bindable_now"
            )
            guarded_bindable_count = sum(
                1 for entry in row_bindings if str(entry.get("binding_posture")) == "guarded_bindable_now"
            )
            blocked_count = sum(
                1
                for entry in row_bindings
                if str(entry.get("binding_posture")) == "row_specific_not_currently_bindable"
            )

            core_trainable_set_rows.append(
                {
                    "symbol": symbol,
                    "truth_tier": row.get("truth_tier"),
                    "cohort_layer": row.get("cohort_layer"),
                    "role_family": row.get("role_family"),
                    "core_trainable_labels": core_labels,
                    "direct_bindable_label_count": direct_bindable_count,
                    "guarded_auxiliary_label_count": guarded_bindable_count,
                    "row_specific_blocked_label_count": blocked_count,
                    "current_stage_windows": row.get("active_stage_windows"),
                    "trainability_posture": "core_skeleton_trainable_now",
                    "reading": (
                        "This row can legally enter an extremely small pilot through the current core label skeleton."
                    ),
                }
            )

        guarded_trainable_set_rows: list[dict[str, Any]] = []
        for label_name in guarded_labels:
            applicable_rows = [
                row
                for row in binding_rows
                if str(row.get("label_name")) == label_name
                and str(row.get("binding_posture")) == "guarded_bindable_now"
            ]
            if not applicable_rows:
                continue
            blocked_rows = [
                row
                for row in binding_rows
                if str(row.get("label_name")) == label_name
                and str(row.get("binding_posture")) == "row_specific_not_currently_bindable"
            ]
            guarded_trainable_set_rows.append(
                {
                    "label_name": label_name,
                    "applicable_symbols": sorted({str(row.get("symbol")) for row in applicable_rows}),
                    "blocked_symbols": sorted({str(row.get("symbol")) for row in blocked_rows}),
                    "guard_type": str(applicable_rows[0].get("support_posture")),
                    "allowed_usage": (
                        "auxiliary_train_signal_only"
                        if label_name != "board_condition_label"
                        else "guarded_auxiliary_or_analysis_label_only"
                    ),
                    "reading": (
                        "This label can enter only as a guarded layer and may not define the pilot on its own."
                    ),
                }
            )

        not_yet_trainable_rows = [
            {
                "item_name": "quiet_window_survival_label",
                "item_type": "label",
                "current_posture": "not_yet_trainable",
                "primary_blocker_layer": "row_geometry",
                "reason": "current truth rows have no explicit quiet-window attachment",
                "reading": "This remains globally meaningful but the current truth geometry does not yet support it.",
            },
            {
                "item_name": "spillover_maturity_boundary_label",
                "item_type": "label",
                "current_posture": "not_yet_trainable",
                "primary_blocker_layer": "row_geometry",
                "reason": "current truth rows exclude late-extension and spillover truth surfaces",
                "reading": "Spillover boundary remains important, but only as overlay or review structure for now.",
            },
            {
                "item_name": "branch_upgrade_label",
                "item_type": "label",
                "current_posture": "review_only_future_target",
                "primary_blocker_layer": "label_binding",
                "reason": "owner review kept it as future-target only",
                "reading": "The concept survives, but not as current pilot supervision.",
            },
            {
                "item_name": "residual_core_vs_collapse_label",
                "item_type": "label",
                "current_posture": "confirmed_only_review",
                "primary_blocker_layer": "label_binding",
                "reason": "it still requires confirmed-only review posture",
                "reading": "This is useful for interpretation and later audit, not for ex-ante pilot truth.",
            },
            {
                "item_name": "board_series_operational_gaps",
                "item_type": "feature_implementation",
                "current_posture": "not_yet_frozen",
                "primary_blocker_layer": "feature_implementation",
                "reason": ", ".join(str(row.get("gap_name")) for row in daily_gap_rows),
                "reading": "Board-conditioned features remain partially ready because the operational table is not fully frozen.",
            },
            {
                "item_name": "future_calendar_operational_gaps",
                "item_type": "feature_implementation",
                "current_posture": "not_yet_frozen",
                "primary_blocker_layer": "feature_implementation",
                "reason": ", ".join(str(row.get("gap_name")) for row in calendar_gap_rows),
                "reading": "Chronology and catalyst-sequence features still depend on an unfinished recurring-calendar rule layer.",
            },
        ]

        layer_readiness_rows = [
            {
                "layer_name": "row_geometry",
                "readiness_posture": "bounded_core_pilot_possible_but_narrow",
                "evidence": {
                    "truth_candidate_row_count": len(truth_rows),
                    "primary_truth_rows": sum(1 for row in truth_rows if str(row.get("truth_tier")) == "primary"),
                    "secondary_truth_rows": sum(1 for row in truth_rows if str(row.get("truth_tier")) == "secondary"),
                    "truth_stage_window_count": len(truth_stage_windows),
                    "has_quiet_window_truth": has_quiet_window_truth,
                    "has_spillover_truth": has_spillover_truth,
                },
                "reading": (
                    "The current geometry is enough for an extremely small core-plus-secondary pilot, but not broad enough "
                    "to claim stage-complete or spillover-complete supervision."
                ),
            },
            {
                "layer_name": "label_binding",
                "readiness_posture": "core_bindable_guarded_auxiliary_only",
                "evidence": {
                    "direct_bindable_count": binding_summary.get("direct_bindable_count"),
                    "guarded_bindable_count": binding_summary.get("guarded_bindable_count"),
                    "row_specific_blocked_count": binding_summary.get("row_specific_blocked_count"),
                    "core_label_count": len(core_labels),
                    "guarded_label_count": len(guarded_labels),
                },
                "reading": (
                    "The pilot has a real supervision skeleton, but it is still uneven: core labels bind cleanly while "
                    "some guarded labels remain subset-only or geometry-blocked."
                ),
            },
            {
                "layer_name": "feature_implementation",
                "readiness_posture": "partial_with_active_operational_gaps",
                "evidence": {
                    "feature_family_count": feature_summary.get("feature_family_count"),
                    "design_ready_feature_count": feature_summary.get("design_ready_feature_count"),
                    "blind_spot_count": feature_summary.get("blind_spot_count"),
                    "daily_board_operational_gap_count": len(daily_gap_rows),
                    "future_calendar_operational_gap_count": len(calendar_gap_rows),
                },
                "reading": (
                    "The design layer is rich enough to support a bounded pilot conceptually, but implementation maturity "
                    "is still the main limiting factor because board and calendar operational rules remain unfinished."
                ),
            },
        ]

        bottleneck_attribution_rows = [
            {
                "layer_name": "feature_implementation",
                "bottleneck_rank": 1,
                "bottleneck_posture": "primary_current_bottleneck",
                "why": (
                    "The core label skeleton exists and the row geometry is sufficient for a tiny pilot, but board and "
                    "calendar operational gaps still make implementation maturity the narrowest legal aperture."
                ),
            },
            {
                "layer_name": "row_geometry",
                "bottleneck_rank": 2,
                "bottleneck_posture": "secondary_bottleneck",
                "why": (
                    "The current truth set covers core and secondary surfaces, but it does not yet include quiet-window "
                    "truth rows or spillover truth rows, so broader representativeness is still missing."
                ),
            },
            {
                "layer_name": "label_binding",
                "bottleneck_rank": 3,
                "bottleneck_posture": "constrained_but_not_primary",
                "why": (
                    "Binding is uneven, but the main core labels already bind cleanly enough for a tiny guarded pilot; "
                    "the larger issue is where and how those bindings can be implemented safely."
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112al_cpo_bounded_training_readiness_review_v1",
            "truth_candidate_row_count": len(truth_rows),
            "truth_stage_window_count": len(truth_stage_windows),
            "core_label_count": len(core_labels),
            "guarded_label_count": len(guarded_labels),
            "direct_bindable_count": binding_summary.get("direct_bindable_count"),
            "guarded_bindable_count": binding_summary.get("guarded_bindable_count"),
            "row_specific_blocked_count": binding_summary.get("row_specific_blocked_count"),
            "design_ready_feature_count": feature_summary.get("design_ready_feature_count"),
            "daily_board_operational_gap_count": len(daily_gap_rows),
            "future_calendar_operational_gap_count": len(calendar_gap_rows),
            "row_geometry_readiness_posture": "bounded_core_pilot_possible_but_narrow",
            "label_binding_readiness_posture": "core_bindable_guarded_auxiliary_only",
            "feature_implementation_readiness_posture": "partial_with_active_operational_gaps",
            "bounded_training_pilot_lawful_now": True,
            "bounded_training_pilot_scope": "extremely_small_core_skeleton_only",
            "representative_training_lawful_now": False,
            "primary_bottleneck_layer": "feature_implementation",
            "secondary_bottleneck_layer": "row_geometry",
            "formal_label_freeze_now": False,
            "formal_training_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "open_extremely_small_core_skeleton_training_pilot_only",
        }
        interpretation = [
            "V1.12AL concludes that a tiny bounded pilot is lawful, but only for the current core skeleton and not for broader representative training.",
            "The project is no longer blocked by the existence of labels alone; it is primarily bottlenecked by implementation maturity and secondarily by still-narrow row geometry.",
            "This review exists to stop both failure modes at once: endless pre-pilot audits and premature training optimism.",
        ]
        return V112ALCPOBoundedTrainingReadinessReviewReport(
            summary=summary,
            layer_readiness_rows=layer_readiness_rows,
            core_trainable_set_rows=core_trainable_set_rows,
            guarded_trainable_set_rows=guarded_trainable_set_rows,
            not_yet_trainable_rows=not_yet_trainable_rows,
            bottleneck_attribution_rows=bottleneck_attribution_rows,
            interpretation=interpretation,
        )


def write_v112al_cpo_bounded_training_readiness_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ALCPOBoundedTrainingReadinessReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
