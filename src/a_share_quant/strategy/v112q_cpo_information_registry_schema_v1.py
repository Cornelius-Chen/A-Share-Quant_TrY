from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112QCPOInformationRegistrySchemaReport:
    summary: dict[str, Any]
    cycle_stage_rows: list[dict[str, Any]]
    information_layer_rows: list[dict[str, Any]]
    bucket_rows: list[dict[str, Any]]
    feature_slot_rows: list[dict[str, Any]]
    subagent_collection_task_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cycle_stage_rows": self.cycle_stage_rows,
            "information_layer_rows": self.information_layer_rows,
            "bucket_rows": self.bucket_rows,
            "feature_slot_rows": self.feature_slot_rows,
            "subagent_collection_task_rows": self.subagent_collection_task_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112QCPOInformationRegistrySchemaAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        registry_payload: dict[str, Any],
        subagent_policy_payload: dict[str, Any],
    ) -> V112QCPOInformationRegistrySchemaReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112q_now")):
            raise ValueError("V1.12Q must be open before schema freeze.")

        registry_summary = dict(registry_payload.get("summary", {}))
        subagent_summary = dict(subagent_policy_payload.get("summary", {}))

        cycle_stage_rows = [
            {
                "stage_name": "pre_ignition_watch",
                "relative_order": 0,
                "minimum_lookback_trading_days": 20,
                "reading": "Collect board, catalyst, and industry context slightly before the visible rise so preheat signals are not lost.",
                "default_collection_priority": "high",
            },
            {
                "stage_name": "ignition",
                "relative_order": 1,
                "minimum_lookback_trading_days": 0,
                "reading": "The point where core names start to detach from background noise and the first clean direction appears.",
                "default_collection_priority": "high",
            },
            {
                "stage_name": "main_markup",
                "relative_order": 2,
                "minimum_lookback_trading_days": 0,
                "reading": "The core trend-acceleration window dominated by leader and mid-core expansion.",
                "default_collection_priority": "high",
            },
            {
                "stage_name": "diffusion",
                "relative_order": 3,
                "minimum_lookback_trading_days": 0,
                "reading": "The stage where adjacent names, branch extensions, and laggard catch-up become active.",
                "default_collection_priority": "high",
            },
            {
                "stage_name": "laggard_catchup",
                "relative_order": 4,
                "minimum_lookback_trading_days": 0,
                "reading": "The later expansion window where lower-quality or delayed names begin to move.",
                "default_collection_priority": "medium",
            },
            {
                "stage_name": "divergence_and_decay",
                "relative_order": 5,
                "minimum_lookback_trading_days": 0,
                "reading": "The phase where the cohort begins to split, leadership quality changes, and some names are abandoned.",
                "default_collection_priority": "high",
            },
        ]

        information_layer_rows = [
            {"layer_name": "industry_technology_path", "layer_goal": "Track the active technical route and which component path is actually being repriced."},
            {"layer_name": "message_and_catalyst", "layer_goal": "Capture public catalyst flow, route debates, and event reinforcement."},
            {"layer_name": "earnings_and_business_performance", "layer_goal": "Track whether the narrative has business or profit validation rather than only theme heat."},
            {"layer_name": "price_and_technical_structure", "layer_goal": "Track the cycle shape, absorption quality, and technical state through the rise and after it."},
            {"layer_name": "stock_role_and_cohort", "layer_goal": "Separate leaders, mid-core names, laggard catch-up, mapping, and pseudo-mapping objects."},
            {"layer_name": "branch_supply_chain_extension", "layer_goal": "Track optical-chip, EML, MPO, FAU, fiber, cable, and equipment branches around the core chain."},
            {"layer_name": "index_sentiment_and_liquidity", "layer_goal": "Track board-level strength, breadth, turnover, sentiment, and cross-board resonance."},
            {"layer_name": "spillover_mixed_relevance_and_noise", "layer_goal": "Preserve weak-relevance, name-bonus, and pure spillover rows for later truth checking."},
            {"layer_name": "time_layered_cycle_attachment", "layer_goal": "Attach every observation to a bounded cycle stage so the same information is not read identically in every phase."},
        ]

        bucket_rows = [
            {"bucket_name": "A_core_seeds_and_leader_mid_core", "allowed_membership": ["validated_core_leader", "validated_core_mid_core"], "reading": "Core seeds and the cleanest leader or mid-core names."},
            {"bucket_name": "B_adjacent_candidates_and_laggard_catchup", "allowed_membership": ["direct_related_review_only", "adjacent_laggard_review_only"], "reading": "Adjacent names, backline names, and laggard catch-up candidates that still need cohort validation."},
            {"bucket_name": "C_supply_chain_branch_extension", "allowed_membership": ["extension_concept_review_only", "chain_extension_review_only"], "reading": "Optical-chip, MPO, FAU, fiber, cable, and equipment branch rows."},
            {"bucket_name": "D_weak_relevance_mapping_name_bonus", "allowed_membership": ["mixed_relevance_spillover_review_only"], "reading": "Weak relevance, pure spillover, and name-bonus rows that may still carry phase information."},
            {"bucket_name": "E_index_sentiment_liquidity_and_event_route", "allowed_membership": ["non_stock_context_rows"], "reading": "Board index, sentiment, liquidity, and route-event chronology rows."},
        ]

        feature_slot_rows = [
            {"layer_name": "industry_technology_path", "feature_slot_name": "technology_route_focus", "feature_role": "route_state", "posture": "review_first"},
            {"layer_name": "industry_technology_path", "feature_slot_name": "component_exposure_eml_inp", "feature_role": "component_exposure", "posture": "review_first"},
            {"layer_name": "industry_technology_path", "feature_slot_name": "component_exposure_mpo_fau", "feature_role": "component_exposure", "posture": "review_first"},
            {"layer_name": "industry_technology_path", "feature_slot_name": "co_packaging_or_pluggable_tilt", "feature_role": "route_preference_proxy", "posture": "review_first"},
            {"layer_name": "message_and_catalyst", "feature_slot_name": "catalyst_type", "feature_role": "catalyst_taxonomy", "posture": "review_first"},
            {"layer_name": "message_and_catalyst", "feature_slot_name": "catalyst_source_quality", "feature_role": "source_quality", "posture": "review_first"},
            {"layer_name": "message_and_catalyst", "feature_slot_name": "catalyst_freshness", "feature_role": "freshness", "posture": "review_first"},
            {"layer_name": "message_and_catalyst", "feature_slot_name": "multi_trigger_resonance", "feature_role": "resonance", "posture": "review_first"},
            {"layer_name": "earnings_and_business_performance", "feature_slot_name": "earnings_acceleration_state", "feature_role": "earnings_proxy", "posture": "review_first"},
            {"layer_name": "earnings_and_business_performance", "feature_slot_name": "gross_margin_direction", "feature_role": "profitability_proxy", "posture": "review_first"},
            {"layer_name": "earnings_and_business_performance", "feature_slot_name": "order_visibility_proxy", "feature_role": "demand_visibility", "posture": "review_first"},
            {"layer_name": "earnings_and_business_performance", "feature_slot_name": "capacity_expansion_signal", "feature_role": "supply_response_proxy", "posture": "review_first"},
            {"layer_name": "price_and_technical_structure", "feature_slot_name": "trend_slope_state", "feature_role": "technical_state", "posture": "review_first"},
            {"layer_name": "price_and_technical_structure", "feature_slot_name": "pullback_depth_state", "feature_role": "technical_state", "posture": "review_first"},
            {"layer_name": "price_and_technical_structure", "feature_slot_name": "high_level_absorption_state", "feature_role": "technical_state", "posture": "review_first"},
            {"layer_name": "price_and_technical_structure", "feature_slot_name": "breakout_reacceleration_state", "feature_role": "technical_state", "posture": "review_first"},
            {"layer_name": "stock_role_and_cohort", "feature_slot_name": "cycle_role_label", "feature_role": "role", "posture": "review_first"},
            {"layer_name": "stock_role_and_cohort", "feature_slot_name": "leader_height_state", "feature_role": "role_strength", "posture": "review_first"},
            {"layer_name": "stock_role_and_cohort", "feature_slot_name": "mid_core_confirmation_state", "feature_role": "role_strength", "posture": "review_first"},
            {"layer_name": "stock_role_and_cohort", "feature_slot_name": "mapping_clarity_level", "feature_role": "role_risk", "posture": "review_first"},
            {"layer_name": "branch_supply_chain_extension", "feature_slot_name": "branch_bucket", "feature_role": "branch_taxonomy", "posture": "review_first"},
            {"layer_name": "branch_supply_chain_extension", "feature_slot_name": "chain_distance_from_core", "feature_role": "branch_distance", "posture": "review_first"},
            {"layer_name": "branch_supply_chain_extension", "feature_slot_name": "branch_rotation_timing", "feature_role": "timing_proxy", "posture": "review_first"},
            {"layer_name": "branch_supply_chain_extension", "feature_slot_name": "component_subtheme_strength", "feature_role": "branch_strength", "posture": "review_first"},
            {"layer_name": "index_sentiment_and_liquidity", "feature_slot_name": "concept_index_strength", "feature_role": "board_state", "posture": "review_first"},
            {"layer_name": "index_sentiment_and_liquidity", "feature_slot_name": "cohort_breadth", "feature_role": "board_state", "posture": "review_first"},
            {"layer_name": "index_sentiment_and_liquidity", "feature_slot_name": "turnover_pressure", "feature_role": "liquidity_state", "posture": "review_first"},
            {"layer_name": "index_sentiment_and_liquidity", "feature_slot_name": "cross_board_resonance", "feature_role": "sentiment_state", "posture": "review_first"},
            {"layer_name": "spillover_mixed_relevance_and_noise", "feature_slot_name": "story_spillover_intensity", "feature_role": "spillover_state", "posture": "review_only"},
            {"layer_name": "spillover_mixed_relevance_and_noise", "feature_slot_name": "name_bonus_risk", "feature_role": "noise_flag", "posture": "review_only"},
            {"layer_name": "spillover_mixed_relevance_and_noise", "feature_slot_name": "weak_relevance_flag", "feature_role": "truth_check_flag", "posture": "review_only"},
            {"layer_name": "spillover_mixed_relevance_and_noise", "feature_slot_name": "board_follow_correlation", "feature_role": "spillover_proxy", "posture": "review_only"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_pre_ignition_watch", "feature_role": "cycle_stage", "posture": "review_first"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_ignition", "feature_role": "cycle_stage", "posture": "review_first"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_main_markup", "feature_role": "cycle_stage", "posture": "review_first"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_diffusion", "feature_role": "cycle_stage", "posture": "review_first"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_laggard_catchup", "feature_role": "cycle_stage", "posture": "review_first"},
            {"layer_name": "time_layered_cycle_attachment", "feature_slot_name": "stage_divergence_decay", "feature_role": "cycle_stage", "posture": "review_first"},
        ]

        subagent_collection_task_rows = [
            {"task_name": "adjacent_official_anchor_harvest", "task_class": "execution", "review_mode": "volume_or_time_based", "used_for": "fill official business and earnings anchors for adjacent cohort rows", "fixed_output_template": "symbol_to_anchor_table", "allowed_scope": "only adjacent and branch-extension cohort rows already frozen in V1.12P", "compute_class": subagent_summary.get("default_compute_class", "low")},
            {"task_name": "branch_extension_official_anchor_harvest", "task_class": "execution", "review_mode": "volume_or_time_based", "used_for": "fill official product and business anchors for MPO, chip, fiber, cable, and equipment branch rows", "fixed_output_template": "branch_anchor_table", "allowed_scope": "only branch_supply_chain_extension rows already frozen in V1.12P", "compute_class": subagent_summary.get("default_compute_class", "low")},
            {"task_name": "daily_concept_index_breadth_turnover_chronology_draft", "task_class": "structuring", "review_mode": "volume_or_time_based", "used_for": "draft where board-level chronology can be sourced and how it should map into the registry", "fixed_output_template": "chronology_source_and_gap_table", "allowed_scope": "only CPO or optical-link board-level rows", "compute_class": subagent_summary.get("default_compute_class", "low")},
            {"task_name": "future_visible_catalyst_calendar_draft", "task_class": "structuring", "review_mode": "volume_or_time_based", "used_for": "draft public forward-visible catalyst anchors such as OFC, GTC, CSP capex, and route events", "fixed_output_template": "future_catalyst_calendar_table", "allowed_scope": "only CPO route-relevant public catalysts", "compute_class": subagent_summary.get("default_compute_class", "low")},
            {"task_name": "mixed_relevance_truth_check_draft", "task_class": "drafting", "review_mode": "stage_based", "used_for": "produce review-only truth-check drafts for weak-relevance or name-bonus rows", "fixed_output_template": "mixed_relevance_review_sheet", "allowed_scope": "only rows already frozen in spillover and mixed-relevance buckets", "compute_class": subagent_summary.get("default_compute_class", "low")},
        ]

        summary = {
            "acceptance_posture": "freeze_v112q_cpo_information_registry_schema_v1",
            "existing_registry_row_count": registry_summary.get("cohort_row_count"),
            "cycle_stage_count": len(cycle_stage_rows),
            "information_layer_count": len(information_layer_rows),
            "bucket_count": len(bucket_rows),
            "feature_slot_count": len(feature_slot_rows),
            "subagent_collection_task_count": len(subagent_collection_task_rows),
            "max_parallel_subagents": subagent_summary.get("max_parallel_subagents"),
            "recommended_parallel_collection_now": 2,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12Q hardens the CPO registry into a traceable schema so omissions become easier to detect and discuss.",
            "Pre-ignition watch coverage is now explicit, which matters because many CPO cycle clues appear before the visible markup window.",
            "A-E buckets prevent core leaders, branch extensions, and noisy spillover rows from being flattened into one object pool.",
            "Subagent work is constrained to repetitive collection drafts; schema naming and acceptance remain on the mainline.",
        ]
        return V112QCPOInformationRegistrySchemaReport(
            summary=summary,
            cycle_stage_rows=cycle_stage_rows,
            information_layer_rows=information_layer_rows,
            bucket_rows=bucket_rows,
            feature_slot_rows=feature_slot_rows,
            subagent_collection_task_rows=subagent_collection_task_rows,
            interpretation=interpretation,
        )


def write_v112q_cpo_information_registry_schema_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112QCPOInformationRegistrySchemaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
