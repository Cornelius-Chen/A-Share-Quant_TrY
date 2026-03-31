from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AACPOBoundedCohortMapReport:
    summary: dict[str, Any]
    object_role_time_rows: list[dict[str, Any]]
    admissibility_rows: list[dict[str, Any]]
    decision_facing_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "object_role_time_rows": self.object_role_time_rows,
            "admissibility_rows": self.admissibility_rows,
            "decision_facing_rows": self.decision_facing_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AACPOBoundedCohortMapAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        reconstruction_payload: dict[str, Any],
        adjacent_validation_payload: dict[str, Any],
        adjacent_split_payload: dict[str, Any],
        spillover_factor_payload: dict[str, Any],
    ) -> V112AACPOBoundedCohortMapReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112aa_now")):
            raise ValueError("V1.12AA must be open before the bounded cohort map is frozen.")

        reconstruction_rows = list(reconstruction_payload.get("role_transition_rows", []))
        if not reconstruction_rows:
            raise ValueError("V1.12AA requires V1.12Z role-transition output.")

        object_role_time_rows = [
            {
                "symbol": "300308",
                "cohort_layer": "core_anchor",
                "role_family": "core_module_leader",
                "active_stage_windows": ["pre_ignition_watch_1", "ignition_1", "main_markup_1", "re_ignition_markup_2", "major_markup_3"],
                "evidence_axes": ["business_purity", "leader_persistence", "earnings_confirmation"],
                "current_posture": "primary_core_truth_row",
            },
            {
                "symbol": "300502",
                "cohort_layer": "core_beta",
                "role_family": "high_beta_core_module",
                "active_stage_windows": ["ignition_1", "main_markup_1", "divergence_decay_1", "major_markup_3"],
                "evidence_axes": ["core_beta_sensitivity", "markup_acceleration", "drawdown_risk_readout"],
                "current_posture": "primary_core_truth_row",
            },
            {
                "symbol": "300394",
                "cohort_layer": "core_platform_confirmation",
                "role_family": "upstream_component_platform",
                "active_stage_windows": ["main_markup_1", "re_ignition_markup_2", "major_markup_3", "divergence_decay_3"],
                "evidence_axes": ["platform_confirmation", "upstream_alignment", "route_depth_confirmation"],
                "current_posture": "primary_core_truth_row",
            },
            {
                "symbol": "002281",
                "cohort_layer": "adjacent_bridge",
                "role_family": "domestic_optics_platform_bridge",
                "active_stage_windows": ["diffusion_1", "re_ignition_markup_2"],
                "evidence_axes": ["domestic_platform_bridge", "diffusion_confirmation"],
                "current_posture": "secondary_review_asset",
            },
            {
                "symbol": "603083",
                "cohort_layer": "adjacent_high_beta_extension",
                "role_family": "high_beta_module_extension",
                "active_stage_windows": ["diffusion_1", "major_markup_3"],
                "evidence_axes": ["beta_extension", "breadth_participation"],
                "current_posture": "secondary_review_asset",
            },
            {
                "symbol": "688205",
                "cohort_layer": "adjacent_high_beta_extension",
                "role_family": "high_end_module_extension",
                "active_stage_windows": ["diffusion_1", "major_markup_3"],
                "evidence_axes": ["high_end_beta_extension", "breadth_participation"],
                "current_posture": "secondary_review_asset",
            },
            {
                "symbol": "301205",
                "cohort_layer": "adjacent_high_beta_extension",
                "role_family": "smaller_cap_high_beta_module",
                "active_stage_windows": ["diffusion_1", "major_markup_3"],
                "evidence_axes": ["small_cap_beta_extension", "crowding_sensitivity"],
                "current_posture": "secondary_review_asset",
            },
            {
                "symbol": "300570",
                "cohort_layer": "branch_extension",
                "role_family": "connector_mpo_branch",
                "active_stage_windows": ["diffusion_1", "laggard_catchup_3"],
                "evidence_axes": ["branch_rotation", "route_granularity"],
                "current_posture": "review_only_branch_asset",
            },
            {
                "symbol": "688498",
                "cohort_layer": "branch_extension",
                "role_family": "laser_chip_component",
                "active_stage_windows": ["re_ignition_markup_2", "major_markup_3"],
                "evidence_axes": ["advanced_component_alignment", "route_depth"],
                "current_posture": "review_only_branch_asset",
            },
            {
                "symbol": "688313",
                "cohort_layer": "branch_extension",
                "role_family": "silicon_photonics_component",
                "active_stage_windows": ["re_ignition_markup_2", "major_markup_3"],
                "evidence_axes": ["advanced_component_alignment", "route_depth"],
                "current_posture": "review_only_branch_asset",
            },
            {
                "symbol": "300757",
                "cohort_layer": "branch_extension",
                "role_family": "packaging_process_enabler",
                "active_stage_windows": ["re_ignition_markup_2", "major_markup_3"],
                "evidence_axes": ["implementation_depth", "process_enabler"],
                "current_posture": "review_only_branch_asset",
            },
            {
                "symbol": "601869",
                "cohort_layer": "late_extension",
                "role_family": "fiber_cable_extension",
                "active_stage_windows": ["laggard_catchup_3"],
                "evidence_axes": ["late_breadth", "stage_maturity"],
                "current_posture": "late_cycle_review_asset",
            },
            {
                "symbol": "600487",
                "cohort_layer": "late_extension",
                "role_family": "fiber_cable_extension",
                "active_stage_windows": ["laggard_catchup_3"],
                "evidence_axes": ["late_breadth", "stage_maturity"],
                "current_posture": "late_cycle_review_asset",
            },
            {
                "symbol": "600522",
                "cohort_layer": "late_extension",
                "role_family": "fiber_cable_extension",
                "active_stage_windows": ["laggard_catchup_3"],
                "evidence_axes": ["late_breadth", "stage_maturity"],
                "current_posture": "late_cycle_review_asset",
            },
            {
                "symbol": "000070",
                "cohort_layer": "spillover_candidate",
                "role_family": "telecom_adjacent_board_follow_factor",
                "active_stage_windows": ["laggard_catchup_3", "divergence_decay_3"],
                "evidence_axes": ["spillover_intensity", "board_follow", "late_stage_signal"],
                "current_posture": "review_only_spillover_candidate",
            },
            {
                "symbol": "603228",
                "cohort_layer": "spillover_candidate",
                "role_family": "hardware_sentiment_spillover_factor",
                "active_stage_windows": ["laggard_catchup_3", "divergence_decay_3"],
                "evidence_axes": ["spillover_intensity", "hardware_sentiment", "late_stage_signal"],
                "current_posture": "review_only_spillover_candidate",
            },
            {
                "symbol": "001267",
                "cohort_layer": "weak_memory",
                "role_family": "name_bonus_or_board_follow_memory",
                "active_stage_windows": ["divergence_decay_3"],
                "evidence_axes": ["weak_name_bonus", "late_cycle_noise"],
                "current_posture": "memory_only_row",
            },
            {
                "symbol": "300620",
                "cohort_layer": "pending_ambiguous",
                "role_family": "upstream_photonics_enabler",
                "active_stage_windows": ["deep_reset_quiet_window"],
                "evidence_axes": ["mixed_enabler", "insufficient_role_clarity"],
                "current_posture": "keep_pending",
            },
            {
                "symbol": "300548",
                "cohort_layer": "pending_ambiguous",
                "role_family": "module_or_silicon_photonics_adjacency",
                "active_stage_windows": ["deep_reset_quiet_window"],
                "evidence_axes": ["mixed_enabler", "insufficient_role_clarity"],
                "current_posture": "keep_pending",
            },
            {
                "symbol": "000988",
                "cohort_layer": "pending_ambiguous",
                "role_family": "vertical_optoelectronic_platform",
                "active_stage_windows": ["deep_reset_quiet_window"],
                "evidence_axes": ["platform_width", "insufficient_role_clarity"],
                "current_posture": "keep_pending",
            },
        ]

        admissibility_rows = [
            {
                "cohort_layer": "core_anchor/core_beta/core_platform_confirmation",
                "later_labeling_posture": "may_enter_primary_labeling_surface",
                "restrictions": "time-bounded only, no leakage, no timeless relabeling",
                "reading": "Core rows are the cleanest candidates for later bounded labeling.",
            },
            {
                "cohort_layer": "adjacent_bridge/adjacent_high_beta_extension",
                "later_labeling_posture": "may_enter_secondary_labeling_surface_after_time-gating",
                "restrictions": "must remain downstream of core stage confirmation",
                "reading": "Adjacents can enter later, but only as secondary objects and only with stage control.",
            },
            {
                "cohort_layer": "branch_extension/late_extension",
                "later_labeling_posture": "review_only_until_specific hypothesis needs them",
                "restrictions": "do not flatten into core cohort",
                "reading": "Branch and late extensions are useful for cycle reading, not automatic truth assignment.",
            },
            {
                "cohort_layer": "spillover_candidate/weak_memory",
                "later_labeling_posture": "keep outside core labeling surface",
                "restrictions": "factor-test or overlay use only",
                "reading": "Spillover is informative, but it is not core optical-link truth.",
            },
            {
                "cohort_layer": "pending_ambiguous",
                "later_labeling_posture": "exclude_from_labeling_until_role is cleaner",
                "restrictions": "must remain explicit, not silently dropped",
                "reading": "Pending rows should not be force-labeled.",
            },
        ]

        decision_facing_rows = [
            {
                "cohort_layer": "core_anchor",
                "best_used_in": "ignition and main markup",
                "preferred_action": "highest conviction attention; first place to concentrate research and future exposure",
            },
            {
                "cohort_layer": "core_beta",
                "best_used_in": "main markup and major markup",
                "preferred_action": "aggressive expression only after core direction is already proven",
            },
            {
                "cohort_layer": "core_platform_confirmation",
                "best_used_in": "main markup, re-ignition, major markup",
                "preferred_action": "use to confirm the cycle is not only a one-factor module chase",
            },
            {
                "cohort_layer": "adjacent_bridge/high_beta_extension",
                "best_used_in": "diffusion and later strong markup windows",
                "preferred_action": "secondary attention; useful for breadth and acceleration, not first ignition truth",
            },
            {
                "cohort_layer": "branch_extension/late_extension",
                "best_used_in": "re-ignition, late catch-up, maturity read",
                "preferred_action": "use as breadth and route-depth context, not as default high-conviction core",
            },
            {
                "cohort_layer": "spillover_candidate/weak_memory",
                "best_used_in": "late catch-up and final divergence",
                "preferred_action": "use mainly as maturity/risk overlay and A-share-specific behavior marker",
            },
            {
                "cohort_layer": "pending_ambiguous",
                "best_used_in": "review only",
                "preferred_action": "do not force into later truth layers until role purity improves",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112aa_cpo_bounded_cohort_map_v1",
            "object_row_count": len(object_role_time_rows),
            "primary_core_truth_row_count": sum(1 for row in object_role_time_rows if row["current_posture"] == "primary_core_truth_row"),
            "secondary_review_asset_count": sum(1 for row in object_role_time_rows if row["current_posture"] == "secondary_review_asset"),
            "review_only_branch_asset_count": sum(1 for row in object_role_time_rows if row["current_posture"] == "review_only_branch_asset"),
            "spillover_or_memory_count": sum(1 for row in object_role_time_rows if row["cohort_layer"] in {"spillover_candidate", "weak_memory"}),
            "pending_ambiguous_count": sum(1 for row in object_role_time_rows if row["cohort_layer"] == "pending_ambiguous"),
            "formal_training_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The cohort map turns the reconstruction narrative into a reusable object-role-time matrix.",
            "It deliberately keeps spillover and pending rows visible, but outside the core truth surface.",
            "This is the right bridge into later labeling review because it hardens boundaries before labels are frozen.",
        ]
        return V112AACPOBoundedCohortMapReport(
            summary=summary,
            object_role_time_rows=object_role_time_rows,
            admissibility_rows=admissibility_rows,
            decision_facing_rows=decision_facing_rows,
            interpretation=interpretation,
        )


def write_v112aa_cpo_bounded_cohort_map_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AACPOBoundedCohortMapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
