from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AFCPOFeatureFamilyDesignReviewReport:
    summary: dict[str, Any]
    feature_family_rows: list[dict[str, Any]]
    feature_design_rows: list[dict[str, Any]]
    suppressed_duplicate_rows: list[dict[str, Any]]
    blind_spot_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_family_rows": self.feature_family_rows,
            "feature_design_rows": self.feature_design_rows,
            "suppressed_duplicate_rows": self.suppressed_duplicate_rows,
            "blind_spot_rows": self.blind_spot_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _feature_row(
    *,
    feature_name: str,
    candidate_tier: str,
    proposed_family: str,
    feature_origin: str,
    point_in_time_definition: str,
    primary_inputs: list[str],
    stage_attachment: list[str],
    admissible_surfaces: list[str],
    duplicate_guard: str,
    anti_leakage_guard: str,
    reading: str,
) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "candidate_tier": candidate_tier,
        "proposed_family": proposed_family,
        "feature_origin": feature_origin,
        "point_in_time_definition": point_in_time_definition,
        "primary_inputs": primary_inputs,
        "stage_attachment": stage_attachment,
        "admissible_surfaces": admissible_surfaces,
        "duplicate_guard": duplicate_guard,
        "anti_leakage_guard": anti_leakage_guard,
        "reading": reading,
    }


class V112AFCPOFeatureFamilyDesignReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        registry_schema_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
        dynamic_role_payload: dict[str, Any],
        brainstorm_payload: dict[str, Any],
    ) -> V112AFCPOFeatureFamilyDesignReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112af_now")):
            raise ValueError("V1.12AF must be open before feature-family design review runs.")

        existing_slots = {
            str(row.get("feature_slot_name"))
            for row in list(registry_schema_payload.get("feature_slot_rows", []))
            if str(row.get("feature_slot_name"))
        }
        if not existing_slots:
            raise ValueError("V1.12AF requires the existing CPO registry feature slots.")

        labeling_surfaces = {
            str(row.get("labeling_surface"))
            for row in list(labeling_review_payload.get("labeling_surface_rows", []))
            if str(row.get("labeling_surface"))
        }
        if "primary_labeling_surface" not in labeling_surfaces:
            raise ValueError("V1.12AF requires V1.12AB labeling surfaces.")

        brainstorm_high_value = {str(name) for name in list(brainstorm_payload.get("high_value_review_candidates", []))}
        suppressed_duplicates = [str(name) for name in list(brainstorm_payload.get("near_duplicates", []))]
        blind_spots = [str(name) for name in list(brainstorm_payload.get("operational_blind_spots", []))]
        dynamic_features = {
            str(row.get("feature_name"))
            for row in list(dynamic_role_payload.get("dynamic_feature_rows", []))
            if str(row.get("feature_name"))
        }

        required_high_value = {
            "anchor_distance_state",
            "window_conflict_state",
            "catalyst_sequence_position_state",
            "expected_realization_slippage_state",
            "quarter_event_alignment_state",
            "relay_handoff_acceptance_state",
            "failed_role_promotion_a_kill_risk_state",
            "board_strength_concentration_divergence_state",
            "core_to_weak_activation_lag_score",
            "quiet_window_survival_gap",
        }
        required_dynamic = {
            "role_persistence_score",
            "challenger_activation_state",
            "role_demotion_risk_state",
            "spillover_saturation_state",
        }
        if not required_high_value.issubset(brainstorm_high_value):
            raise ValueError("V1.12AF requires the full V1.12AE high-value shortlist.")
        if not required_dynamic.issubset(dynamic_features):
            raise ValueError("V1.12AF requires the key V1.12AD dynamic anchors.")

        feature_family_rows = [
            {
                "family_name": "chronology_time_geometry_family",
                "design_goal": "Turn event timing into explicit geometry and conflict states.",
                "core_members": [
                    "anchor_distance_state",
                    "window_conflict_state",
                    "expected_realization_slippage_state",
                    "quarter_event_alignment_state",
                ],
                "extends_existing_slots": [
                    "anchor_event_overlap_daily",
                    "post_event_followthrough_window",
                    "between_event_quiet_window",
                    "post_earnings_reset_window",
                ],
            },
            {
                "family_name": "catalyst_sequence_family",
                "design_goal": "Track where a catalyst sits in the cycle rather than only whether it exists.",
                "core_members": [
                    "catalyst_sequence_position_state",
                    "capex_confirmation_delay_state",
                    "design_win_conversion_maturity_state",
                    "standards_to_commercial_conversion_state",
                ],
                "extends_existing_slots": [
                    "catalyst_type",
                    "catalyst_freshness",
                    "multi_trigger_resonance",
                    "capacity_expansion_signal",
                ],
            },
            {
                "family_name": "dynamic_role_handoff_family",
                "design_goal": "Represent role persistence, activation, handoff, demotion, and failed promotion.",
                "core_members": [
                    "relay_handoff_acceptance_state",
                    "failed_role_promotion_a_kill_risk_state",
                    "role_persistence_score",
                    "challenger_activation_state",
                    "role_demotion_risk_state",
                    "role_transition_vacancy_duration",
                ],
                "extends_existing_slots": [
                    "cycle_role_label",
                    "leader_height_state",
                    "mid_core_confirmation_state",
                ],
            },
            {
                "family_name": "board_structure_divergence_family",
                "design_goal": "Separate healthy board breadth from concentration, spread, and shock propagation.",
                "core_members": [
                    "board_strength_concentration_divergence_state",
                    "core_challenger_leadership_spread_state",
                    "anchor_shock_propagation_state",
                ],
                "extends_existing_slots": [
                    "concept_index_strength",
                    "cohort_breadth",
                    "turnover_pressure",
                    "cross_board_resonance",
                ],
            },
            {
                "family_name": "spillover_maturity_decay_family",
                "design_goal": "Treat weak activation and spillover as maturity diagnostics instead of core truth.",
                "core_members": [
                    "core_to_weak_activation_lag_score",
                    "quiet_window_survival_gap",
                    "spillover_saturation_state",
                    "role_path_break_flag",
                ],
                "extends_existing_slots": [
                    "story_spillover_intensity",
                    "board_follow_correlation",
                    "high_level_absorption_state",
                ],
            },
            {
                "family_name": "overlay_boundary_family",
                "design_goal": "Preserve weak-cohort and name-bonus overlays without leaking into core truth.",
                "core_members": [
                    "event_decoupled_weak_breadth_ratio",
                    "weak_turnover_migration_gap",
                    "board_heat_elasticity_asymmetry",
                    "lexical_name_bonus_without_role_path_score",
                ],
                "extends_existing_slots": [
                    "name_bonus_risk",
                    "weak_relevance_flag",
                    "story_spillover_intensity",
                ],
            },
        ]

        feature_design_rows = [
            _feature_row(
                feature_name="anchor_distance_state",
                candidate_tier="design_ready_review_candidate",
                proposed_family="chronology_time_geometry_family",
                feature_origin="v112ae_high_value_shortlist",
                point_in_time_definition="Signed trading-day distance to the nearest active public anchor known on that date.",
                primary_inputs=["anchor_event_overlap_daily", "future_catalyst_calendar", "current_trade_date"],
                stage_attachment=["pre_ignition_watch", "ignition", "main_markup", "re_ignition_markup"],
                admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                duplicate_guard="Not a duplicate of anchor_event_overlap_daily; overlap is binary while distance is geometry.",
                anti_leakage_guard="Only anchors already public by the row date are allowed.",
                reading="Distinguishes preheat, fresh event response, and stale follow-through.",
            ),
            _feature_row(
                feature_name="window_conflict_state",
                candidate_tier="design_ready_review_candidate",
                proposed_family="chronology_time_geometry_family",
                feature_origin="v112ae_high_value_shortlist",
                point_in_time_definition="Flags conflicting earnings, conference, capex, and quiet windows.",
                primary_inputs=["post_event_followthrough_window", "between_event_quiet_window", "post_earnings_reset_window", "future_catalyst_calendar"],
                stage_attachment=["pre_ignition_watch", "divergence_and_decay", "deep_reset_quiet_window", "major_markup"],
                admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                duplicate_guard="Not a duplicate of multi_trigger_resonance; conflict is not the same as resonance.",
                anti_leakage_guard="Only currently open windows may contribute.",
                reading="Separates clean continuation from crowded contradictory timing.",
            ),
            _feature_row(
                feature_name="catalyst_sequence_position_state",
                candidate_tier="design_ready_review_candidate",
                proposed_family="catalyst_sequence_family",
                feature_origin="v112ae_high_value_shortlist",
                point_in_time_definition="Places the current catalyst thread in a bounded sequence from preheat to residual memory.",
                primary_inputs=["catalyst_type", "catalyst_freshness", "anchor_distance_state", "current_cycle_stage"],
                stage_attachment=["pre_ignition_watch", "ignition", "main_markup", "diffusion", "laggard_catchup", "divergence_and_decay"],
                admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                duplicate_guard="Not a duplicate of catalyst_freshness_state; age is not the same as cycle position.",
                anti_leakage_guard="Sequence position must use only chronology visible by the row date.",
                reading="Separates ignition catalysts from late narrative echoes.",
            ),
            _feature_row(
                feature_name="expected_realization_slippage_state",
                candidate_tier="design_ready_review_candidate",
                proposed_family="chronology_time_geometry_family",
                feature_origin="v112ae_high_value_shortlist",
                point_in_time_definition="Measures whether realization is arriving earlier, on time, or later than the public story implies.",
                primary_inputs=["launch_to_ramp_window", "design_win_to_volume_window", "order_visibility_proxy", "post_event_followthrough_window"],
                stage_attachment=["pre_ignition_watch", "main_markup", "deep_reset_quiet_window", "re_ignition_markup"],
                admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                duplicate_guard="Not a duplicate of launch_to_ramp_window; this is mismatch, not one window.",
                anti_leakage_guard="Only currently available guideposts and updates are allowed.",
                reading="Useful when the story runs ahead of commercialization or confirmation arrives early.",
            ),
            _feature_row(
                feature_name="quarter_event_alignment_state",
                candidate_tier="design_ready_review_candidate",
                proposed_family="chronology_time_geometry_family",
                feature_origin="v112ae_high_value_shortlist",
                point_in_time_definition="Marks whether the current phase is aligned or misaligned with the reporting-quarter cadence.",
                primary_inputs=["pre_earnings_channel_check_window", "post_earnings_reset_window", "quarter_identifier", "current_cycle_stage"],
                stage_attachment=["pre_ignition_watch", "main_markup", "deep_reset_quiet_window", "major_markup"],
                admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                duplicate_guard="Not a duplicate of the earnings windows; it binds quarter cadence to cycle stage.",
                anti_leakage_guard="Use scheduled cadence and already released results only.",
                reading="Tells whether the phase runs with quarter support or against quarter timing.",
            ),
        ]

        feature_design_rows.extend(
            [
                _feature_row(
                    feature_name="relay_handoff_acceptance_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ae_high_value_shortlist",
                    point_in_time_definition="Measures whether a challenger is truly accepted by the board after core leadership widens.",
                    primary_inputs=["challenger_activation_state", "cohort_breadth_daily", "concept_index_strength_daily", "turnover_pressure_daily"],
                    stage_attachment=["diffusion", "re_ignition_markup", "major_markup"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="Not a duplicate of challenger_activation_state; activation is not acceptance.",
                    anti_leakage_guard="Acceptance must be inferred from same-window board evidence, not later returns.",
                    reading="Separates valid relay behavior from one-day adjacent noise.",
                ),
                _feature_row(
                    feature_name="failed_role_promotion_a_kill_risk_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ae_high_value_shortlist",
                    point_in_time_definition="Marks a failed promotion attempt that is vulnerable to sharp downside.",
                    primary_inputs=["role_demotion_risk_state", "turnover_pressure_daily", "high_level_absorption_state", "board_strength_concentration_divergence_state"],
                    stage_attachment=["divergence_and_decay", "major_markup", "final_decay"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                    duplicate_guard="Not a duplicate of role_demotion_risk_state; this is the sharper failed-promotion case.",
                    anti_leakage_guard="Use live pressure and failed-acceptance signals only.",
                    reading="A drawdown-control feature for false second-wave candidates.",
                ),
                _feature_row(
                    feature_name="board_strength_concentration_divergence_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="board_structure_divergence_family",
                    feature_origin="v112ae_high_value_shortlist",
                    point_in_time_definition="Captures whether board strength is broad and healthy or increasingly concentrated.",
                    primary_inputs=["concept_index_strength_daily", "cohort_breadth_daily", "turnover_pressure_daily", "cross_board_resonance_daily"],
                    stage_attachment=["diffusion", "major_markup", "laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                    duplicate_guard="Not a duplicate of cohort_breadth_daily; breadth level is not internal concentration.",
                    anti_leakage_guard="Use same-day board aggregates only.",
                    reading="Separates healthy strength from late-stage narrowing.",
                ),
                _feature_row(
                    feature_name="core_to_weak_activation_lag_score",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="spillover_maturity_decay_family",
                    feature_origin="v112ae_high_value_shortlist",
                    point_in_time_definition="Measures how long after core activation weak rows begin to respond.",
                    primary_inputs=["core_activation_dates", "story_spillover_intensity", "board_follow_correlation", "current_trade_date"],
                    stage_attachment=["diffusion", "laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["review_support_surface", "overlay_only_surface"],
                    duplicate_guard="Not a duplicate of story_spillover_intensity; this is lag geometry.",
                    anti_leakage_guard="Lag is computed only against already observed core activation dates.",
                    reading="Separates healthy widening from tired late weak activation.",
                ),
                _feature_row(
                    feature_name="quiet_window_survival_gap",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="spillover_maturity_decay_family",
                    feature_origin="v112ae_high_value_shortlist",
                    point_in_time_definition="Measures the quiet-window survival gap between stronger and weaker rows.",
                    primary_inputs=["between_event_quiet_window", "high_level_absorption_state", "turnover_pressure_daily", "role_persistence_score"],
                    stage_attachment=["deep_reset_quiet_window", "divergence_and_decay"],
                    admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface", "overlay_only_surface"],
                    duplicate_guard="Not a duplicate of high_level_absorption_state; this is cross-cohort survival quality.",
                    anti_leakage_guard="Use only current quiet-window behavior; later restart success is forbidden.",
                    reading="Highlights which rows deserve later requalification after long quiet windows.",
                ),
                _feature_row(
                    feature_name="role_persistence_score",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ad_dynamic_role_review",
                    point_in_time_definition="Measures whether a row maintains the same useful role across adjacent stage windows.",
                    primary_inputs=["current_role_family", "previous_stage_role_family", "current_cycle_stage"],
                    stage_attachment=["ignition", "main_markup", "diffusion", "re_ignition_markup", "major_markup"],
                    admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="New dynamic anchor; no exact duplicate exists in the static role schema.",
                    anti_leakage_guard="Only already-passed stage-local transitions may contribute.",
                    reading="Separates stable leaders from flash-in-the-pan breakouts.",
                ),
                _feature_row(
                    feature_name="challenger_activation_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ad_dynamic_role_review",
                    point_in_time_definition="Marks when adjacent rows move from passive relevance to active diffusion participation.",
                    primary_inputs=["cycle_role_label", "cohort_breadth_daily", "current_cycle_stage"],
                    stage_attachment=["diffusion", "re_ignition_markup", "major_markup"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="Existing dynamic anchor that should stay distinct from relay_handoff_acceptance_state.",
                    anti_leakage_guard="Activation must be judged from the current stage and board support only.",
                    reading="The first positive gate before relay acceptance.",
                ),
                _feature_row(
                    feature_name="role_demotion_risk_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ad_dynamic_role_review",
                    point_in_time_definition="Captures whether a row is losing role quality during divergence before a full price collapse.",
                    primary_inputs=["current_role_family", "turnover_pressure_daily", "high_level_absorption_state", "board_strength_concentration_divergence_state"],
                    stage_attachment=["divergence_and_decay", "major_markup", "final_decay"],
                    admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="Existing dynamic anchor that pairs with failed_role_promotion_a_kill_risk_state.",
                    anti_leakage_guard="Must be defined from live structure degradation only.",
                    reading="Recognizes rows that still look strong but are no longer role-clean.",
                ),
                _feature_row(
                    feature_name="spillover_saturation_state",
                    candidate_tier="design_ready_review_candidate",
                    proposed_family="spillover_maturity_decay_family",
                    feature_origin="v112ad_dynamic_role_review",
                    point_in_time_definition="Marks when spillover stops adding breadth information and starts indicating maturity.",
                    primary_inputs=["story_spillover_intensity", "board_follow_correlation", "cohort_breadth_daily", "current_cycle_stage"],
                    stage_attachment=["laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["overlay_only_surface", "review_support_surface"],
                    duplicate_guard="Existing dynamic anchor that should remain separate from core truth.",
                    anti_leakage_guard="Use current spillover participation only; later collapse cannot be fed back.",
                    reading="Tells when late breadth is maturity information instead of opportunity.",
                ),
            ]
        )

        feature_design_rows.extend(
            [
                _feature_row(
                    feature_name="capex_confirmation_delay_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="catalyst_sequence_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Measures whether expected capex reinforcement is arriving later than the public narrative expects.",
                    primary_inputs=["future_catalyst_calendar", "order_visibility_proxy", "capacity_expansion_signal"],
                    stage_attachment=["pre_ignition_watch", "main_markup", "deep_reset_quiet_window"],
                    admissible_surfaces=["primary_labeling_surface", "secondary_labeling_surface"],
                    duplicate_guard="May overlap with expected_realization_slippage_state until capex anchor rules are tighter.",
                    anti_leakage_guard="Use visible capex guidance and already released commentary only.",
                    reading="Keep speculative until calendar rollforward rules are harder.",
                ),
                _feature_row(
                    feature_name="design_win_conversion_maturity_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="catalyst_sequence_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Tracks where a design-win story sits on the path from announcement to volume.",
                    primary_inputs=["design_win_to_volume_window", "launch_to_ramp_window", "order_visibility_proxy"],
                    stage_attachment=["pre_ignition_watch", "re_ignition_markup", "major_markup"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="May overlap with launch_to_ramp_window until design-win source discipline is standardized.",
                    anti_leakage_guard="Only design wins already public by the row date may contribute.",
                    reading="Keep speculative until more adjacent business anchors are normalized.",
                ),
                _feature_row(
                    feature_name="quiet_window_tension_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="chronology_time_geometry_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Marks whether a quiet window is constructive tension or only fatigue masking.",
                    primary_inputs=["between_event_quiet_window", "turnover_pressure_daily", "quiet_window_survival_gap"],
                    stage_attachment=["deep_reset_quiet_window", "divergence_and_decay"],
                    admissible_surfaces=["review_support_surface"],
                    duplicate_guard="Likely overlaps with quiet_window_survival_gap until board vendor and turnover rules are frozen.",
                    anti_leakage_guard="No later breakout or failure outcome may label the tension state.",
                    reading="Keep speculative because it stays close to a later narrative judgment.",
                ),
                _feature_row(
                    feature_name="standards_to_commercial_conversion_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="catalyst_sequence_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Tracks the lag between standards or route discussion and tradeable commercialization.",
                    primary_inputs=["technology_route_focus", "conference_or_standard_anchor", "launch_to_ramp_window"],
                    stage_attachment=["pre_ignition_watch", "re_ignition_markup"],
                    admissible_surfaces=["review_support_surface"],
                    duplicate_guard="Needs route-standard anchors to be more explicit before it can be separated from general catalyst sequencing.",
                    anti_leakage_guard="Only public route or standard milestones available at that date may be used.",
                    reading="Keep speculative until route-standard event coverage is deeper.",
                ),
                _feature_row(
                    feature_name="post_event_decay_half_life_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="chronology_time_geometry_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Measures how quickly event-driven strength decays after the event window closes.",
                    primary_inputs=["post_event_followthrough_window", "concept_index_strength_daily", "relative_strength_series"],
                    stage_attachment=["main_markup", "diffusion", "major_markup"],
                    admissible_surfaces=["review_support_surface"],
                    duplicate_guard="Overlaps with anchor_distance_state and expected_realization_slippage_state until decay rules are standardized.",
                    anti_leakage_guard="Only already elapsed sessions after the event may be used.",
                    reading="Keep speculative until a more stable decay measurement rule exists.",
                ),
                _feature_row(
                    feature_name="core_challenger_leadership_spread_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="board_structure_divergence_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Measures the spread between core leader strength and accepted challenger strength.",
                    primary_inputs=["leader_retention_state", "challenger_activation_state", "cohort_breadth_daily"],
                    stage_attachment=["diffusion", "major_markup"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="May overlap with relay_handoff_acceptance_state and board_strength_concentration_divergence_state.",
                    anti_leakage_guard="Only current accepted challengers count; no later winner selection allowed.",
                    reading="Keep speculative until relay and board concentration definitions settle.",
                ),
                _feature_row(
                    feature_name="anchor_shock_propagation_state",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="board_structure_divergence_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Measures how strongly an anchor shock propagates across adjacent, branch, and spillover layers.",
                    primary_inputs=["leader_retention_state", "cohort_breadth_daily", "cross_board_resonance_daily", "story_spillover_intensity"],
                    stage_attachment=["divergence_and_decay", "major_markup", "final_decay"],
                    admissible_surfaces=["review_support_surface", "overlay_only_surface"],
                    duplicate_guard="Needs frozen breadth and turnover formulas before it can avoid becoming a loose narrative restatement.",
                    anti_leakage_guard="Propagation must be measured in currently visible same-window reactions only.",
                    reading="Keep speculative until board operational rules are harder.",
                ),
                _feature_row(
                    feature_name="role_transition_vacancy_duration",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="dynamic_role_handoff_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Counts how long a role slot stays vacant between one accepted holder and the next.",
                    primary_inputs=["role_persistence_score", "challenger_activation_state", "relay_handoff_acceptance_state"],
                    stage_attachment=["diffusion", "deep_reset_quiet_window", "re_ignition_markup"],
                    admissible_surfaces=["secondary_labeling_surface", "review_support_surface"],
                    duplicate_guard="Needs more explicit from-role and to-role event recording before it becomes stable.",
                    anti_leakage_guard="Vacancy can only use elapsed observed windows, not future handoff completion.",
                    reading="Keep speculative until transition-event granularity is richer.",
                ),
                _feature_row(
                    feature_name="role_path_break_flag",
                    candidate_tier="keep_as_speculative_family_member",
                    proposed_family="spillover_maturity_decay_family",
                    feature_origin="v112ae_speculative_shortlist",
                    point_in_time_definition="Flags when a row stops resembling any legitimate core, adjacent, or branch progression.",
                    primary_inputs=["cycle_role_label", "role_persistence_score", "core_to_weak_activation_lag_score", "board_follow_correlation"],
                    stage_attachment=["laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["overlay_only_surface", "review_support_surface"],
                    duplicate_guard="Potentially overlaps with weak_relevance_flag until alias and concept-tag structure are better defined.",
                    anti_leakage_guard="The break flag must be inferred from path inconsistency already visible by the row date.",
                    reading="Keep speculative because it depends on a still-missing name and concept-tag layer.",
                ),
                _feature_row(
                    feature_name="event_decoupled_weak_breadth_ratio",
                    candidate_tier="overlay_only_candidate",
                    proposed_family="overlay_boundary_family",
                    feature_origin="v112ae_overlay_only_shortlist",
                    point_in_time_definition="Measures how much weak breadth appears without direct event alignment.",
                    primary_inputs=["cohort_breadth_daily", "anchor_distance_state", "weak_relevance_flag"],
                    stage_attachment=["laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["overlay_only_surface"],
                    duplicate_guard="Overlay-only by design; it should not compete with core board strength features.",
                    anti_leakage_guard="Only same-window breadth and anchor visibility may be used.",
                    reading="A-share noise overlay candidate, not a core truth feature.",
                ),
                _feature_row(
                    feature_name="weak_turnover_migration_gap",
                    candidate_tier="overlay_only_candidate",
                    proposed_family="overlay_boundary_family",
                    feature_origin="v112ae_overlay_only_shortlist",
                    point_in_time_definition="Tracks whether turnover is migrating from stronger rows into weak or noisy rows.",
                    primary_inputs=["turnover_pressure_daily", "cohort_layer_distribution", "story_spillover_intensity"],
                    stage_attachment=["laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["overlay_only_surface"],
                    duplicate_guard="Requires frozen turnover normalization before any upgrade beyond overlay-only is discussable.",
                    anti_leakage_guard="Use same-day turnover migration only.",
                    reading="Late-cycle overlay candidate for A-share maturity and risk.",
                ),
                _feature_row(
                    feature_name="board_heat_elasticity_asymmetry",
                    candidate_tier="overlay_only_candidate",
                    proposed_family="overlay_boundary_family",
                    feature_origin="v112ae_overlay_only_shortlist",
                    point_in_time_definition="Measures whether weak rows respond more elastically to board heat than strong rows.",
                    primary_inputs=["concept_index_strength_daily", "cohort_breadth_daily", "story_spillover_intensity"],
                    stage_attachment=["diffusion", "laggard_catchup"],
                    admissible_surfaces=["overlay_only_surface"],
                    duplicate_guard="Likely overlaps with core_to_weak_activation_lag_score until weaker-row activation rules are more stable.",
                    anti_leakage_guard="Only same-window elasticity may be measured.",
                    reading="Overlay-only because it is more about A-share noise elasticity than business purity.",
                ),
                _feature_row(
                    feature_name="lexical_name_bonus_without_role_path_score",
                    candidate_tier="overlay_only_candidate",
                    proposed_family="overlay_boundary_family",
                    feature_origin="v112ae_overlay_only_shortlist",
                    point_in_time_definition="Scores when a row benefits from name overlap without a coherent role path.",
                    primary_inputs=["name_bonus_risk", "board_follow_correlation", "role_path_break_flag"],
                    stage_attachment=["laggard_catchup", "divergence_and_decay"],
                    admissible_surfaces=["overlay_only_surface"],
                    duplicate_guard="Cannot be upgraded until a dedicated name, alias, and concept-tag structure exists.",
                    anti_leakage_guard="Only contemporaneous naming and concept-tag evidence may be used.",
                    reading="Pure overlay candidate to preserve A-share lexical spillover without poisoning core truth.",
                ),
            ]
        )

        suppressed_duplicate_rows = [
            {
                "feature_name": feature_name,
                "status": "suppress_as_duplicate_or_overlapping_candidate",
                "reading": "Kept out of the design-ready list because the current schema or stronger shortlist already covers most of its signal family.",
            }
            for feature_name in suppressed_duplicates
        ]
        blind_spot_rows = [
            {
                "blind_spot_name": name,
                "why_preserved": "This remains an explicit operational gap and should not be hidden by the new feature-family design.",
                "recommended_next_use": "preserve_as_follow_up_gap",
            }
            for name in blind_spots
        ]

        summary = {
            "acceptance_posture": "freeze_v112af_cpo_feature_family_design_review_v1",
            "existing_feature_slot_count": len(existing_slots),
            "feature_family_count": len(feature_family_rows),
            "design_ready_feature_count": sum(1 for row in feature_design_rows if row["candidate_tier"] == "design_ready_review_candidate"),
            "speculative_feature_count": sum(1 for row in feature_design_rows if row["candidate_tier"] == "keep_as_speculative_family_member"),
            "overlay_only_feature_count": sum(1 for row in feature_design_rows if row["candidate_tier"] == "overlay_only_candidate"),
            "suppressed_duplicate_count": len(suppressed_duplicate_rows),
            "blind_spot_count": len(blind_spot_rows),
            "formal_feature_promotion_still_forbidden": True,
            "formal_label_freeze_still_forbidden": True,
            "formal_training_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The strongest additions are now compressed into six feature families rather than staying as a flat brainstorm list.",
            "The current design-ready layer is dominated by chronology geometry, role handoff, and spillover maturity rather than generic alpha fantasies.",
            "Overlay-only candidates remain explicit and bounded; they are preserved because they may carry A-share-specific stage information, not because they are core truth.",
            "The next lawful move is bounded label-draft assembly with these families as governed candidate inputs, not automatic feature promotion.",
        ]
        return V112AFCPOFeatureFamilyDesignReviewReport(
            summary=summary,
            feature_family_rows=feature_family_rows,
            feature_design_rows=feature_design_rows,
            suppressed_duplicate_rows=suppressed_duplicate_rows,
            blind_spot_rows=blind_spot_rows,
            interpretation=interpretation,
        )


def write_v112af_cpo_feature_family_design_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AFCPOFeatureFamilyDesignReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
