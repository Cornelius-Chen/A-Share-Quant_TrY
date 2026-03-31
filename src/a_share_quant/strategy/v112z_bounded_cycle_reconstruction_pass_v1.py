from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZBoundedCycleReconstructionPassReport:
    summary: dict[str, Any]
    reconstructed_stage_rows: list[dict[str, Any]]
    catalyst_order_rows: list[dict[str, Any]]
    role_transition_rows: list[dict[str, Any]]
    board_overlay_rows: list[dict[str, Any]]
    spillover_overlay_rows: list[dict[str, Any]]
    residual_ambiguity_rows: list[dict[str, Any]]
    owner_facing_reconstruction_summary: list[str]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reconstructed_stage_rows": self.reconstructed_stage_rows,
            "catalyst_order_rows": self.catalyst_order_rows,
            "role_transition_rows": self.role_transition_rows,
            "board_overlay_rows": self.board_overlay_rows,
            "spillover_overlay_rows": self.spillover_overlay_rows,
            "residual_ambiguity_rows": self.residual_ambiguity_rows,
            "owner_facing_reconstruction_summary": self.owner_facing_reconstruction_summary,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ZBoundedCycleReconstructionPassAnalyzer:
    def analyze(
        self,
        *,
        operational_charter_payload: dict[str, Any],
        protocol_payload: dict[str, Any],
        registry_schema_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        adjacent_validation_payload: dict[str, Any],
        chronology_payload: dict[str, Any],
        daily_board_payload: dict[str, Any],
        future_calendar_payload: dict[str, Any],
        spillover_truth_payload: dict[str, Any],
        spillover_factor_payload: dict[str, Any],
        adjacent_split_payload: dict[str, Any],
    ) -> V112ZBoundedCycleReconstructionPassReport:
        charter_summary = dict(operational_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_reconstruction_pass")):
            raise ValueError("V1.12Z operational charter must be frozen before the reconstruction pass runs.")

        protocol_summary = dict(protocol_payload.get("summary", {}))
        if not bool(protocol_summary.get("foundation_ready_for_bounded_cycle_reconstruction")):
            raise ValueError("V1.12Z protocol must confirm bounded reconstruction readiness.")

        dataset_rows = list(pilot_dataset_payload.get("dataset_rows", []))
        if len(dataset_rows) != 3:
            raise ValueError("The bounded reconstruction pass expects the frozen three-symbol core optical-link pilot.")

        core_symbols = [str(row.get("symbol")) for row in dataset_rows]
        validated_adjacent_rows = [
            row
            for row in list(adjacent_validation_payload.get("validation_rows", []))
            if str(row.get("review_disposition", "")).startswith("validate_as_")
        ]
        split_ready_adjacent_rows = [
            row
            for row in list(adjacent_split_payload.get("probe_rows", []))
            if str(row.get("review_candidacy_status")) == "keep_as_split_ready_review_asset"
        ]
        pending_adjacent_rows = [
            row
            for row in list(adjacent_split_payload.get("probe_rows", []))
            if str(row.get("review_candidacy_status", "")).startswith("keep_pending_")
        ]
        spillover_factor_rows = list(spillover_factor_payload.get("factor_review_rows", []))
        chronology_rows = list(chronology_payload.get("chronology_segment_rows", []))
        board_series_rows = list(daily_board_payload.get("daily_series_rows", []))
        future_calendar_rows = list(future_calendar_payload.get("recurring_calendar_rows", []))

        reconstructed_stage_rows = [
            {
                "occurrence_name": "pre_ignition_watch_1",
                "stage_family": "pre_ignition_watch",
                "window": "2023-01 to 2023-02",
                "primary_symbols": core_symbols,
                "dominant_reading": "AI-capex and optical-demand expectation drift matters before the obvious breakout.",
                "supporting_context": [
                    "pre_earnings_channel_check_window",
                    "capex_to_order_conversion_window",
                    "conference_or_route_event watch",
                ],
            },
            {
                "occurrence_name": "ignition_1",
                "stage_family": "ignition",
                "window": "2023-02 to 2023-03",
                "primary_symbols": ["300308", "300502"],
                "dominant_reading": "Core module names detach first; leadership quality matters more than breadth.",
                "supporting_context": [
                    "concept_index_strength_daily",
                    "cross_board_resonance_daily",
                    "catalyst_freshness",
                ],
            },
            {
                "occurrence_name": "main_markup_1",
                "stage_family": "main_markup",
                "window": "2023-03 to 2023-06",
                "primary_symbols": ["300308", "300502", "300394"],
                "dominant_reading": "The first clean markup is led by core optical-module beneficiaries and confirmed by the upstream component platform.",
                "supporting_context": [
                    "earnings_acceleration_state",
                    "order_visibility_proxy",
                    "event_window and post_event_followthrough_window",
                ],
            },
            {
                "occurrence_name": "diffusion_1",
                "stage_family": "diffusion",
                "window": "2023-05 to 2023-09",
                "primary_symbols": ["603083", "688205", "301205", "002281", "300570"],
                "dominant_reading": "High-beta challengers, domestic optics bridges, and connector/MPO branches activate after the core markup proves durable.",
                "supporting_context": [
                    "cohort_breadth_daily",
                    "branch_rotation_timing",
                    "multi_trigger_resonance",
                ],
            },
            {
                "occurrence_name": "divergence_decay_1",
                "stage_family": "divergence_and_decay",
                "window": "2023-07 to 2024-01",
                "primary_symbols": ["300308", "300502", "603083", "688205"],
                "dominant_reading": "The first wave stops being a one-direction story; some names hold structure while others reveal role-quality differences.",
                "supporting_context": [
                    "high_level_absorption_state",
                    "between_event_quiet_window",
                    "turnover_pressure_daily",
                ],
            },
            {
                "occurrence_name": "re_ignition_markup_2",
                "stage_family": "main_markup",
                "window": "2024-02 to 2024-06",
                "primary_symbols": ["300308", "300502", "300394", "688498", "688313"],
                "dominant_reading": "A secondary reacceleration emerges as route discussion, core earnings, and advanced-component adjacency reinforce each other.",
                "supporting_context": [
                    "launch_to_ramp_window",
                    "design_win_to_volume_window",
                    "advanced component branch adjacency",
                ],
            },
            {
                "occurrence_name": "deep_reset_quiet_window",
                "stage_family": "divergence_and_decay",
                "window": "2024-07 to 2025-05",
                "primary_symbols": ["300308", "300394", "000988", "300620", "300548"],
                "dominant_reading": "A long quiet or deep-reset period separates structural beneficiaries from rows that only looked good during the first diffusion burst.",
                "supporting_context": [
                    "between_event_quiet_window",
                    "post_earnings_reset_window",
                    "capex_to_order_conversion_window",
                ],
            },
            {
                "occurrence_name": "major_markup_3",
                "stage_family": "main_markup",
                "window": "2025-06 to 2026-01",
                "primary_symbols": ["300308", "300502", "300394", "603083", "688205", "301205"],
                "dominant_reading": "The strongest integrated wave combines core leader strength, challenger beta, and broader board resonance under a cleaner optical-link narrative.",
                "supporting_context": [
                    "concept_index_strength_daily",
                    "cross_board_resonance_daily",
                    "quarterly_csp_results_or_capex_anchor",
                ],
            },
            {
                "occurrence_name": "laggard_catchup_3",
                "stage_family": "laggard_catchup",
                "window": "2025-08 to 2026-02",
                "primary_symbols": ["601869", "600487", "600522", "000070", "603228"],
                "dominant_reading": "Fiber-cable extensions and A-share spillover candidates become more informative about stage maturity than about core business purity.",
                "supporting_context": [
                    "cohort_breadth_daily",
                    "story_spillover_intensity",
                    "board_follow_correlation",
                ],
            },
            {
                "occurrence_name": "divergence_decay_3",
                "stage_family": "divergence_and_decay",
                "window": "2026-02 to 2026-03",
                "primary_symbols": ["300308", "300502", "300394", "000070", "603228", "001267"],
                "dominant_reading": "The final stage separates residual core strength from spillover collapse and weak name-bonus memory.",
                "supporting_context": [
                    "pullback_depth_state",
                    "turnover_pressure_daily",
                    "post_event_followthrough_window",
                ],
            },
        ]

        catalyst_order_rows = [
            {
                "order_id": 1,
                "catalyst_thread": "hyperscaler_ai_capex_and_optical_demand_expectation",
                "first_dominant_stage": "pre_ignition_watch_1",
                "role_in_cycle": "preheat_and_ignition_context",
            },
            {
                "order_id": 2,
                "catalyst_thread": "conference_and_route_event_reinforcement",
                "first_dominant_stage": "ignition_1",
                "role_in_cycle": "initial_public_narrative_reinforcement",
            },
            {
                "order_id": 3,
                "catalyst_thread": "core_earnings_acceleration_and_guidance_confirmation",
                "first_dominant_stage": "main_markup_1",
                "role_in_cycle": "fundamental_confirmation",
            },
            {
                "order_id": 4,
                "catalyst_thread": "advanced_component_and_branch_extension_activation",
                "first_dominant_stage": "diffusion_1",
                "role_in_cycle": "cohort_widening_and_route_granularity",
            },
            {
                "order_id": 5,
                "catalyst_thread": "board_liquidity_and_cross_hardware_resonance",
                "first_dominant_stage": "major_markup_3",
                "role_in_cycle": "amplifier",
            },
            {
                "order_id": 6,
                "catalyst_thread": "spillover_and_name_bonus_late_cycle_behavior",
                "first_dominant_stage": "laggard_catchup_3",
                "role_in_cycle": "late_stage_maturity_indicator",
            },
        ]

        role_transition_rows = [
            {
                "symbol": "300308",
                "role_family": "core_module_leader",
                "stage_progression": ["pre_ignition_watch_1", "ignition_1", "main_markup_1", "re_ignition_markup_2", "major_markup_3"],
                "reading": "The cleanest leader anchor and the main benchmark for whether the cycle is still alive.",
            },
            {
                "symbol": "300502",
                "role_family": "high_beta_core_module",
                "stage_progression": ["ignition_1", "main_markup_1", "divergence_decay_1", "major_markup_3"],
                "reading": "The strongest high-beta core expression and the best aggression barometer.",
            },
            {
                "symbol": "300394",
                "role_family": "upstream_component_platform",
                "stage_progression": ["main_markup_1", "re_ignition_markup_2", "major_markup_3", "divergence_decay_3"],
                "reading": "The upstream platform confirms that the cycle is not only a module beta story.",
            },
            {
                "symbol": "002281",
                "role_family": "domestic_optics_platform_bridge",
                "stage_progression": ["diffusion_1", "re_ignition_markup_2"],
                "reading": "Useful during diffusion and secondary strengthening, not the first ignition anchor.",
            },
            {
                "symbol": "603083/688205/301205",
                "role_family": "high_beta_module_extension_cluster",
                "stage_progression": ["diffusion_1", "major_markup_3"],
                "reading": "Challenge-beta rows that help capture widened module enthusiasm after the core story is proven.",
            },
            {
                "symbol": "300570",
                "role_family": "connector_mpo_branch",
                "stage_progression": ["diffusion_1", "laggard_catchup_3"],
                "reading": "Connector and MPO branch matters once the market pays for route granularity.",
            },
            {
                "symbol": "688498/688313",
                "role_family": "advanced_component_cluster",
                "stage_progression": ["re_ignition_markup_2", "major_markup_3"],
                "reading": "Advanced component adjacency matters more when route depth becomes market-relevant.",
            },
            {
                "symbol": "300757",
                "role_family": "packaging_process_enabler",
                "stage_progression": ["re_ignition_markup_2", "major_markup_3"],
                "reading": "Packaging and process adjacency becomes visible later, once implementation depth matters.",
            },
            {
                "symbol": "601869/600487/600522",
                "role_family": "fiber_cable_extension",
                "stage_progression": ["laggard_catchup_3"],
                "reading": "Useful for late-cycle breadth and maturity, not for defining the cycle start.",
            },
            {
                "symbol": "000070/603228",
                "role_family": "a_share_spillover_factor_candidates",
                "stage_progression": ["laggard_catchup_3", "divergence_decay_3"],
                "reading": "Useful as A-share-specific spillover indicators rather than business-pure truth rows.",
            },
            {
                "symbol": "001267",
                "role_family": "weak_name_bonus_memory",
                "stage_progression": ["divergence_decay_3"],
                "reading": "Marks the weakest end of the spillover surface.",
            },
        ]

        board_overlay_rows = [
            {
                "series_name": "concept_index_strength_daily",
                "most_informative_stages": ["ignition_1", "main_markup_1", "major_markup_3"],
            },
            {
                "series_name": "cohort_breadth_daily",
                "most_informative_stages": ["diffusion_1", "laggard_catchup_3"],
            },
            {
                "series_name": "turnover_pressure_daily",
                "most_informative_stages": ["divergence_decay_1", "major_markup_3", "divergence_decay_3"],
            },
            {
                "series_name": "cross_board_resonance_daily",
                "most_informative_stages": ["ignition_1", "major_markup_3"],
            },
            {
                "series_name": "anchor_event_overlap_daily",
                "most_informative_stages": ["pre_ignition_watch_1", "main_markup_1", "re_ignition_markup_2"],
            },
        ]

        spillover_overlay_rows = [
            {
                "symbol": row.get("symbol"),
                "review_bucket": row.get("candidate_factor_family"),
                "best_read_as": "late_cycle_stage_indicator"
                if row.get("review_candidacy_status") == "keep_as_bounded_a_share_spillover_factor_candidate"
                else "weak_memory_only",
                "do_not_confuse_with": "core_earnings_transmission_truth",
                "reading": row.get("reading"),
            }
            for row in spillover_factor_rows
        ]

        residual_ambiguity_rows = [
            {
                "ambiguity_name": row.get("symbol"),
                "ambiguity_family": "pending_adjacent_role_split",
                "current_posture": row.get("review_candidacy_status"),
                "why_preserved": row.get("reading"),
            }
            for row in pending_adjacent_rows
        ] + [
            {
                "ambiguity_name": row.get("gap_name"),
                "ambiguity_family": "board_operational_gap",
                "current_posture": "preserve_as_operational_gap",
                "why_preserved": row.get("why_it_still_matters"),
            }
            for row in list(daily_board_payload.get("unresolved_gap_rows", []))
        ] + [
            {
                "ambiguity_name": row.get("gap_name"),
                "ambiguity_family": "calendar_operational_gap",
                "current_posture": "preserve_as_operational_gap",
                "why_preserved": row.get("why_it_still_matters"),
            }
            for row in list(future_calendar_payload.get("unresolved_gap_rows", []))
        ]

        owner_facing_reconstruction_summary = [
            "The optical-link cycle is not one smooth trend; it is best read as pre-ignition watch, first ignition and markup, diffusion, reset, re-ignition, major late markup, and final divergence.",
            "300308 remains the cleanest leader anchor, 300502 is the strongest high-beta core expression, and 300394 is the upstream platform that prevents the cycle from collapsing into a one-factor story.",
            "Adjacent names matter, but they do not all matter in the same phase: challengers and domestic optics bridges belong to diffusion, while advanced-component and process rows become more useful in re-ignition and later markup windows.",
            "Spillover rows should not be discarded; they are late-cycle maturity and A-share noise indicators, not core business truth rows.",
            "Board strength, breadth, turnover, and cross-board resonance are amplifiers and maturity indicators, not substitutes for core role identification.",
            "The current reconstruction is strong enough to support bounded cohort mapping and bounded labeling review, but not strong enough to authorize automatic training or signal logic.",
        ]

        summary = {
            "acceptance_posture": "freeze_v112z_bounded_cycle_reconstruction_pass_v1",
            "reconstructed_stage_window_count": len(reconstructed_stage_rows),
            "catalyst_thread_count": len(catalyst_order_rows),
            "role_transition_count": len(role_transition_rows),
            "board_overlay_count": len(board_overlay_rows),
            "spillover_overlay_count": len(spillover_overlay_rows),
            "residual_ambiguity_count": len(residual_ambiguity_rows),
            "core_seed_count": len(core_symbols),
            "validated_adjacent_review_asset_count": len(validated_adjacent_rows),
            "split_ready_adjacent_review_asset_count": len(split_ready_adjacent_rows),
            "chronology_segment_count": len(chronology_rows),
            "daily_board_series_count": len(board_series_rows),
            "future_catalyst_anchor_count": len(future_calendar_rows),
            "cycle_absorption_review_success": True,
            "formal_training_still_forbidden": True,
            "execution_still_forbidden": True,
            "ready_for_owner_review_next": True,
            "recommended_next_posture": "owner_review_then_bounded_cohort_map_or_labeling_pilot",
        }
        interpretation = [
            "The bounded reconstruction pass closes the gap between cleaned information layers and an owner-facing cycle narrative.",
            "The pass preserves unresolved adjacent, board, and calendar ambiguity instead of pretending the cycle is fully purified.",
            "This is a review-only cycle map: strong enough to support the next bounded research layer, but not a license for auto-training or signal generation.",
        ]
        return V112ZBoundedCycleReconstructionPassReport(
            summary=summary,
            reconstructed_stage_rows=reconstructed_stage_rows,
            catalyst_order_rows=catalyst_order_rows,
            role_transition_rows=role_transition_rows,
            board_overlay_rows=board_overlay_rows,
            spillover_overlay_rows=spillover_overlay_rows,
            residual_ambiguity_rows=residual_ambiguity_rows,
            owner_facing_reconstruction_summary=owner_facing_reconstruction_summary,
            interpretation=interpretation,
        )


def write_v112z_bounded_cycle_reconstruction_pass_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZBoundedCycleReconstructionPassReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
