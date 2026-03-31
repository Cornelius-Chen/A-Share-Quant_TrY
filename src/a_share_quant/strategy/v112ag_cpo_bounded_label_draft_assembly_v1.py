from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AGCPOBoundedLabelDraftAssemblyReport:
    summary: dict[str, Any]
    label_surface_skeleton_rows: list[dict[str, Any]]
    family_support_matrix_rows: list[dict[str, Any]]
    anti_leakage_review_rows: list[dict[str, Any]]
    ambiguity_preservation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_surface_skeleton_rows": self.label_surface_skeleton_rows,
            "family_support_matrix_rows": self.family_support_matrix_rows,
            "anti_leakage_review_rows": self.anti_leakage_review_rows,
            "ambiguity_preservation_rows": self.ambiguity_preservation_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _label_row(
    *,
    label_name: str,
    label_layer: str,
    intended_reading: str,
    allowed_surfaces: list[str],
    admissible_object_layers: list[str],
    role_dynamics_needed: list[str],
    reading: str,
) -> dict[str, Any]:
    return {
        "label_name": label_name,
        "label_layer": label_layer,
        "intended_reading": intended_reading,
        "allowed_surfaces": allowed_surfaces,
        "admissible_object_layers": admissible_object_layers,
        "role_dynamics_needed": role_dynamics_needed,
        "reading": reading,
    }


class V112AGCPOBoundedLabelDraftAssemblyAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cohort_map_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
        dynamic_role_payload: dict[str, Any],
        feature_family_payload: dict[str, Any],
    ) -> V112AGCPOBoundedLabelDraftAssemblyReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ag_now")):
            raise ValueError("V1.12AG must be open before bounded label-draft assembly runs.")

        cohort_rows = list(cohort_map_payload.get("object_role_time_rows", []))
        surface_rows = list(labeling_review_payload.get("labeling_surface_rows", []))
        dynamic_rows = list(dynamic_role_payload.get("dynamic_feature_rows", []))
        family_rows = list(feature_family_payload.get("feature_family_rows", []))
        feature_rows = list(feature_family_payload.get("feature_design_rows", []))
        if not cohort_rows:
            raise ValueError("V1.12AG requires the V1.12AA cohort map rows.")
        if not surface_rows:
            raise ValueError("V1.12AG requires the V1.12AB labeling surfaces.")
        if not dynamic_rows:
            raise ValueError("V1.12AG requires the V1.12AD dynamic role layer.")
        if not family_rows or not feature_rows:
            raise ValueError("V1.12AG requires the V1.12AF feature-family review.")

        design_ready_features = {
            str(row.get("feature_name"))
            for row in feature_rows
            if str(row.get("candidate_tier")) == "design_ready_review_candidate"
        }
        dynamic_feature_names = {
            str(row.get("feature_name"))
            for row in dynamic_rows
            if str(row.get("feature_name"))
        }
        family_names = {str(row.get("family_name")) for row in family_rows if str(row.get("family_name"))}

        required_design_ready = {
            "anchor_distance_state",
            "window_conflict_state",
            "catalyst_sequence_position_state",
            "expected_realization_slippage_state",
            "relay_handoff_acceptance_state",
            "failed_role_promotion_a_kill_risk_state",
            "board_strength_concentration_divergence_state",
            "quiet_window_survival_gap",
            "role_persistence_score",
            "role_demotion_risk_state",
        }
        required_dynamic = {
            "branch_upgrade_state",
            "residual_core_strength_state",
            "spillover_collapse_risk_state",
            "role_transition_confidence_state",
        }
        required_families = {
            "chronology_time_geometry_family",
            "catalyst_sequence_family",
            "dynamic_role_handoff_family",
            "board_structure_divergence_family",
            "spillover_maturity_decay_family",
            "overlay_boundary_family",
        }
        if not required_design_ready.issubset(design_ready_features):
            raise ValueError("V1.12AG requires the V1.12AF design-ready feature layer.")
        if not required_dynamic.issubset(dynamic_feature_names):
            raise ValueError("V1.12AG requires the dynamic role features needed for guarded labels.")
        if not required_families.issubset(family_names):
            raise ValueError("V1.12AG requires all six V1.12AF feature families.")

        surface_symbols: dict[str, list[str]] = {}
        for row in surface_rows:
            surface = str(row.get("labeling_surface"))
            symbol = str(row.get("symbol"))
            if surface and symbol:
                surface_symbols.setdefault(surface, []).append(symbol)

        label_surface_skeleton_rows = [
            _label_row(
                label_name="phase_progression_label",
                label_layer="phase_related_label",
                intended_reading="Bounded phase placement across ignition, markup, diffusion, quiet-window, laggard catch-up, and decay transitions.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension", "branch_extension", "late_extension"],
                role_dynamics_needed=["anchor_distance_state", "window_conflict_state", "quarter_event_alignment_state"],
                reading="This is the chronology backbone; it should remain phase language, not become a generic strength label.",
            ),
            _label_row(
                label_name="role_state_label",
                label_layer="role_related_label",
                intended_reading="Current role family at a bounded point in time, with explicit room for pending and review-only states.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension", "branch_extension", "late_extension"],
                role_dynamics_needed=["role_persistence_score", "challenger_activation_state", "role_transition_confidence_state"],
                reading="This is the stable role language, but it must preserve that roles are time-conditioned and may downgrade.",
            ),
            _label_row(
                label_name="role_transition_label",
                label_layer="role_related_label",
                intended_reading="Promotion, handoff, demotion, or failed transition between role states.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension", "branch_extension"],
                role_dynamics_needed=["relay_handoff_acceptance_state", "role_demotion_risk_state", "role_transition_confidence_state"],
                reading="This is where dynamic role handoff becomes label language, but only with guarded provisional vs confirmed posture.",
            ),
            _label_row(
                label_name="catalyst_sequence_label",
                label_layer="phase_related_label",
                intended_reading="Where the currently visible catalyst sits inside the cycle rather than whether a catalyst exists at all.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension", "branch_extension"],
                role_dynamics_needed=["catalyst_sequence_position_state", "expected_realization_slippage_state"],
                reading="This prevents all public news from being flattened into one catalyst-on flag.",
            ),
            _label_row(
                label_name="board_condition_label",
                label_layer="board_condition_label",
                intended_reading="Healthy breadth, concentration, divergence, or pressure condition at board level.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "adjacent_high_beta_extension", "branch_extension", "late_extension", "spillover_candidate", "weak_memory"],
                role_dynamics_needed=["board_strength_concentration_divergence_state"],
                reading="Board state must stay distinct from role state and spillover maturity.",
            ),
            _label_row(
                label_name="quiet_window_survival_label",
                label_layer="phase_related_label",
                intended_reading="Whether a row remains constructively alive through a quiet or reset window.",
                allowed_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "adjacent_bridge", "branch_extension", "pending_ambiguous"],
                role_dynamics_needed=["quiet_window_survival_gap", "role_persistence_score"],
                reading="This is valuable but leakage-sensitive; it cannot be treated as instant truth without a provisional guard.",
            ),
            _label_row(
                label_name="failed_role_promotion_label",
                label_layer="role_related_label",
                intended_reading="Attempted upward role move that fails and shifts into elevated A-kill or sharp drawdown risk.",
                allowed_surfaces=["secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                admissible_object_layers=["adjacent_high_beta_extension", "branch_extension", "late_extension", "spillover_candidate"],
                role_dynamics_needed=["failed_role_promotion_a_kill_risk_state", "role_demotion_risk_state"],
                reading="This keeps false second-wave stories out of clean continuation language.",
            ),
            _label_row(
                label_name="branch_upgrade_label",
                label_layer="role_related_label",
                intended_reading="Branch or component row that upgrades into a stronger cycle role through route-depth confirmation.",
                allowed_surfaces=["secondary_labeling_surface", "review_support_surface"],
                admissible_object_layers=["branch_extension", "adjacent_bridge", "pending_ambiguous"],
                role_dynamics_needed=["branch_upgrade_state", "relay_handoff_acceptance_state"],
                reading="This is intentionally narrower than simple extension strength.",
            ),
            _label_row(
                label_name="spillover_maturity_boundary_label",
                label_layer="spillover_boundary_label",
                intended_reading="Boundary between informative late-cycle spillover and non-core lexical or board-follow noise.",
                allowed_surfaces=["review_support_surface", "overlay_only_surface"],
                admissible_object_layers=["late_extension", "spillover_candidate", "weak_memory"],
                role_dynamics_needed=["core_to_weak_activation_lag_score", "spillover_saturation_state"],
                reading="This label exists to preserve A-share spillover information without promoting it to core truth.",
            ),
            _label_row(
                label_name="residual_core_vs_collapse_label",
                label_layer="spillover_boundary_label",
                intended_reading="Late-cycle distinction between residual core strength and spillover-led collapse.",
                allowed_surfaces=["review_support_surface", "overlay_only_surface"],
                admissible_object_layers=["core_anchor", "core_beta", "core_platform_confirmation", "late_extension", "spillover_candidate", "weak_memory"],
                role_dynamics_needed=["residual_core_strength_state", "spillover_collapse_risk_state", "role_transition_confidence_state"],
                reading="This is strategically valuable for exits, but it is also the label most likely to overread hindsight.",
            ),
        ]

        family_support_matrix_rows = [
            {
                "label_name": "phase_progression_label",
                "primary_support_family": "chronology_time_geometry_family",
                "secondary_support_families": ["catalyst_sequence_family"],
                "explicit_supporting_features": ["anchor_distance_state", "window_conflict_state", "quarter_event_alignment_state", "catalyst_sequence_position_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_now",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                "reading": "Phase placement is now supported by real chronology geometry rather than pure narrative time slicing.",
            },
            {
                "label_name": "role_state_label",
                "primary_support_family": "dynamic_role_handoff_family",
                "secondary_support_families": ["chronology_time_geometry_family"],
                "explicit_supporting_features": ["role_persistence_score", "challenger_activation_state", "role_transition_confidence_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_now",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                "reading": "Role state is supportable, but only if role confidence and time-conditioning remain explicit.",
            },
            {
                "label_name": "role_transition_label",
                "primary_support_family": "dynamic_role_handoff_family",
                "secondary_support_families": ["board_structure_divergence_family"],
                "explicit_supporting_features": ["relay_handoff_acceptance_state", "role_demotion_risk_state", "role_transition_confidence_state", "board_strength_concentration_divergence_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_with_provisional_guard",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                "reading": "Transitions are supportable, but must remain provisional until handoff acceptance is observable in-window.",
            },
            {
                "label_name": "catalyst_sequence_label",
                "primary_support_family": "catalyst_sequence_family",
                "secondary_support_families": ["chronology_time_geometry_family"],
                "explicit_supporting_features": ["catalyst_sequence_position_state", "expected_realization_slippage_state", "anchor_distance_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_now",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                "reading": "Catalyst sequence is no longer a flat freshness proxy.",
            },
            {
                "label_name": "board_condition_label",
                "primary_support_family": "board_structure_divergence_family",
                "secondary_support_families": ["chronology_time_geometry_family"],
                "explicit_supporting_features": ["board_strength_concentration_divergence_state", "window_conflict_state"],
                "weak_or_missing_support": ["breadth_formula_not_yet_frozen", "turnover_normalization_rule_not_yet_frozen"],
                "support_posture": "supported_with_known_operational_gaps",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                "reading": "Board condition is usable, but still partially bottlenecked by the frozen-series rules that remain unfinished.",
            },
            {
                "label_name": "quiet_window_survival_label",
                "primary_support_family": "spillover_maturity_decay_family",
                "secondary_support_families": ["chronology_time_geometry_family", "dynamic_role_handoff_family"],
                "explicit_supporting_features": ["quiet_window_survival_gap", "role_persistence_score", "window_conflict_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_with_provisional_guard",
                "admissible_surfaces": ["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                "reading": "Survival through quiet windows is informative, but too close to hindsight to be treated as instant truth.",
            },
            {
                "label_name": "failed_role_promotion_label",
                "primary_support_family": "dynamic_role_handoff_family",
                "secondary_support_families": ["board_structure_divergence_family"],
                "explicit_supporting_features": ["failed_role_promotion_a_kill_risk_state", "role_demotion_risk_state", "board_strength_concentration_divergence_state"],
                "weak_or_missing_support": [],
                "support_posture": "supported_with_provisional_guard",
                "admissible_surfaces": ["secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                "reading": "The family support is strong enough for a draft label, but only under tight anti-leakage review.",
            },
            {
                "label_name": "branch_upgrade_label",
                "primary_support_family": "dynamic_role_handoff_family",
                "secondary_support_families": ["catalyst_sequence_family"],
                "explicit_supporting_features": ["branch_upgrade_state", "relay_handoff_acceptance_state", "catalyst_sequence_position_state"],
                "weak_or_missing_support": ["pending adjacent role split rows remain unresolved for 300620/300548/000988"],
                "support_posture": "review_only_until_more_support",
                "admissible_surfaces": ["secondary_labeling_surface", "review_support_surface"],
                "reading": "This label is plausible, but the unresolved branch and platform rows mean it cannot be treated as a clean draft truth yet.",
            },
            {
                "label_name": "spillover_maturity_boundary_label",
                "primary_support_family": "spillover_maturity_decay_family",
                "secondary_support_families": ["overlay_boundary_family", "board_structure_divergence_family"],
                "explicit_supporting_features": ["core_to_weak_activation_lag_score", "spillover_saturation_state", "board_strength_concentration_divergence_state"],
                "weak_or_missing_support": ["name_alias_concept_tag_layer_missing"],
                "support_posture": "supported_with_overlay_boundary_guard",
                "admissible_surfaces": ["review_support_surface", "overlay_only_surface"],
                "reading": "This can be drafted, but only if overlay and lexical spillover remain explicitly bounded.",
            },
            {
                "label_name": "residual_core_vs_collapse_label",
                "primary_support_family": "spillover_maturity_decay_family",
                "secondary_support_families": ["dynamic_role_handoff_family", "board_structure_divergence_family"],
                "explicit_supporting_features": ["residual_core_strength_state", "spillover_collapse_risk_state", "role_transition_confidence_state", "board_strength_concentration_divergence_state"],
                "weak_or_missing_support": ["turnover_normalization_rule_not_yet_frozen", "breadth_formula_not_yet_frozen"],
                "support_posture": "confirmed_only_review_label",
                "admissible_surfaces": ["review_support_surface", "overlay_only_surface"],
                "reading": "This label is strategically useful, but it still reads too close to post-outcome structure to become an ex-ante draft truth.",
            },
        ]

        anti_leakage_review_rows = [
            {
                "label_name": "phase_progression_label",
                "point_in_time_posture": "needs_provisional_confirmed_split",
                "future_dependency_risk": "phase edges can drift if later board outcomes are allowed to redefine the current window",
                "recommended_guard": "allow provisional phase labels in-window and only confirm phase completion after the next public chronology segment begins",
                "reading": "Phase language is powerful, but phase certainty can still be quietly backfilled.",
            },
            {
                "label_name": "role_state_label",
                "point_in_time_posture": "ex_ante_usable_with_pending_preservation",
                "future_dependency_risk": "medium if pending rows are force-fit to make the table cleaner",
                "recommended_guard": "keep pending and weak-confidence role states explicit instead of coercing them into core families",
                "reading": "Role state is the safest major label so long as ambiguity survives.",
            },
            {
                "label_name": "role_transition_label",
                "point_in_time_posture": "needs_provisional_confirmed_split",
                "future_dependency_risk": "high because handoff success often becomes obvious only after follow-through",
                "recommended_guard": "split provisional role transition from confirmed role transition and require same-window acceptance evidence",
                "reading": "Role transitions are especially prone to hindsight compression.",
            },
            {
                "label_name": "catalyst_sequence_label",
                "point_in_time_posture": "ex_ante_usable",
                "future_dependency_risk": "medium if sequence position is inferred from later commercialization instead of current public order",
                "recommended_guard": "sequence position may use only public chronology, public anchor dates, and current known commercialization status",
                "reading": "This label is usable because the sequence is defined against public anchor order, not future price response.",
            },
            {
                "label_name": "board_condition_label",
                "point_in_time_posture": "ex_ante_usable_with_formula_guard",
                "future_dependency_risk": "medium because formula drift can change historical readings later",
                "recommended_guard": "freeze formula versions when labeling and do not retrofit board state after formula updates",
                "reading": "Board labels are time-safe only if the board aggregates themselves stop moving under the hood.",
            },
            {
                "label_name": "quiet_window_survival_label",
                "point_in_time_posture": "needs_provisional_confirmed_split",
                "future_dependency_risk": "high because survival sounds point-in-time but often depends on what happens after the quiet window",
                "recommended_guard": "use provisional quiet-window resilience in-window and reserve survival confirmation for post-window review only",
                "reading": "This is the clearest example of a label that can look ex-ante while quietly consuming future structure.",
            },
            {
                "label_name": "failed_role_promotion_label",
                "point_in_time_posture": "needs_provisional_confirmed_split",
                "future_dependency_risk": "high because failure is often recognized only after the fade or A-kill",
                "recommended_guard": "allow attempted promotion and promotion-at-risk ex-ante; reserve failed-promotion confirmation for later review",
                "reading": "This label is too useful to drop, but too hindsight-sensitive to leave unguarded.",
            },
            {
                "label_name": "branch_upgrade_label",
                "point_in_time_posture": "needs_provisional_confirmed_split",
                "future_dependency_risk": "medium-high because branch upgrade often looks obvious only after route depth is confirmed",
                "recommended_guard": "keep branch-upgrade draft labels provisional until current route-depth and role handoff evidence align",
                "reading": "Good candidate label, but not yet clean enough to pretend it is current truth in all rows.",
            },
            {
                "label_name": "spillover_maturity_boundary_label",
                "point_in_time_posture": "ex_ante_usable_with_overlay_boundary",
                "future_dependency_risk": "medium because late-cycle spillover can be mistaken for healthy diffusion if lexical noise is not preserved",
                "recommended_guard": "forbid overlay-only rows from being auto-promoted into secondary or primary surfaces",
                "reading": "This label is safer when its purpose stays diagnostic rather than promotive.",
            },
            {
                "label_name": "residual_core_vs_collapse_label",
                "point_in_time_posture": "confirmed_only",
                "future_dependency_risk": "very high because collapse and residual survival are outcome-heavy distinctions",
                "recommended_guard": "keep this label as confirmed-only review language and exclude it from ex-ante draft truth surfaces",
                "reading": "This label is valuable for review and exits, but not honest as an ex-ante draft truth today.",
            },
        ]

        ambiguity_preservation_rows = [
            {
                "ambiguity_state_name": "pending_ambiguous_row_preservation",
                "applies_to_symbols": surface_symbols.get("excluded_pending_surface", []),
                "applies_to_surface": "excluded_pending_surface",
                "preservation_rule": "retain explicit pending rows and forbid forced assignment into clean draft labels",
                "training_posture": "excluded_pending_surface_only",
                "reading": "The pending rows are not a defect in the draft; they are part of the truth-preserving boundary.",
            },
            {
                "ambiguity_state_name": "overlay_only_spillover_preservation",
                "applies_to_symbols": surface_symbols.get("overlay_only_surface", []),
                "applies_to_surface": "overlay_only_surface",
                "preservation_rule": "keep spillover and weak-memory rows diagnostic, not promotive",
                "training_posture": "overlay_only_review_memory",
                "reading": "A-share spillover may be informative, but it should not silently become core truth.",
            },
            {
                "ambiguity_state_name": "secondary_surface_weak_confidence_preservation",
                "applies_to_symbols": surface_symbols.get("secondary_labeling_surface", []),
                "applies_to_surface": "secondary_labeling_surface",
                "preservation_rule": "allow secondary labels to remain bounded and confidence-scored rather than core-ized",
                "training_posture": "secondary_bounded_review_surface",
                "reading": "Secondary rows are useful draft inputs, but they still need bounded confidence rather than full truth posture.",
            },
            {
                "ambiguity_state_name": "review_support_branch_preservation",
                "applies_to_symbols": surface_symbols.get("review_support_surface", []),
                "applies_to_surface": "review_support_surface",
                "preservation_rule": "preserve branch, late-extension, and support rows as support-only unless later evidence justifies elevation",
                "training_posture": "review_support_only",
                "reading": "Support rows exist to retain cycle context, not to bulk up the truth surface.",
            },
            {
                "ambiguity_state_name": "provisional_transition_label_preservation",
                "applies_to_symbols": [],
                "applies_to_surface": "cross_surface_guard",
                "preservation_rule": "all transition-like labels may carry provisional and confirmed variants instead of one forced verdict",
                "training_posture": "provisional_then_confirmed_review_only",
                "reading": "Transition and survival language should preserve temporal uncertainty rather than hide it.",
            },
            {
                "ambiguity_state_name": "confirmed_only_decay_preservation",
                "applies_to_symbols": [],
                "applies_to_surface": "review_support_surface_and_overlay_only_surface",
                "preservation_rule": "keep collapse-style labels confirmed-only until board and turnover formulas are fully stabilized",
                "training_posture": "confirmed_review_only",
                "reading": "Late-cycle collapse and residual strength remain too outcome-sensitive for ex-ante draft truth.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112ag_cpo_bounded_label_draft_assembly_v1",
            "label_skeleton_count": len(label_surface_skeleton_rows),
            "family_support_mapping_count": len(family_support_matrix_rows),
            "anti_leakage_review_count": len(anti_leakage_review_rows),
            "ambiguity_preservation_count": len(ambiguity_preservation_rows),
            "labels_supported_now_count": sum(1 for row in family_support_matrix_rows if row["support_posture"] == "supported_now"),
            "labels_supported_with_guard_count": sum(
                1
                for row in family_support_matrix_rows
                if row["support_posture"] in {
                    "supported_with_provisional_guard",
                    "supported_with_known_operational_gaps",
                    "supported_with_overlay_boundary_guard",
                }
            ),
            "labels_review_only_or_confirmed_only_count": sum(
                1
                for row in family_support_matrix_rows
                if row["support_posture"] in {"review_only_until_more_support", "confirmed_only_review_label"}
            ),
            "formal_label_freeze_still_forbidden": True,
            "formal_training_still_forbidden": True,
            "formal_signal_generation_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12AG succeeds only if labels, cohort layers, dynamic roles, and feature families can be assembled without hiding ambiguity.",
            "The strongest labels are now supported by explicit families rather than pure narrative intuition.",
            "Several strategically attractive labels still need provisional-versus-confirmed posture instead of pretending to be instant truth.",
            "The next lawful move is review of the bounded draft integrity, not automatic training.",
        ]
        return V112AGCPOBoundedLabelDraftAssemblyReport(
            summary=summary,
            label_surface_skeleton_rows=label_surface_skeleton_rows,
            family_support_matrix_rows=family_support_matrix_rows,
            anti_leakage_review_rows=anti_leakage_review_rows,
            ambiguity_preservation_rows=ambiguity_preservation_rows,
            interpretation=interpretation,
        )


def write_v112ag_cpo_bounded_label_draft_assembly_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AGCPOBoundedLabelDraftAssemblyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
