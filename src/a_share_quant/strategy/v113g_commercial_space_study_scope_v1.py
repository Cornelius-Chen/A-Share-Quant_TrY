from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113GCommercialSpaceStudyScopeReport:
    summary: dict[str, Any]
    study_scope: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "study_scope": self.study_scope,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113GCommercialSpaceStudyScopeAnalyzer:
    """Freeze the first deep-study registry for commercial-space mainline."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_object_pool_payload: dict[str, Any],
    ) -> V113GCommercialSpaceStudyScopeReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v113g_now")):
            raise ValueError("V1.13G must be open before study-scope freeze.")

        pilot_objects = list(pilot_object_pool_payload.get("object_rows", []))
        validated_symbols = {str(row.get("symbol", "")) for row in pilot_objects}

        study_scope = {
            "selected_archetype": "commercial_space_mainline",
            "why_high_value_now": [
                "multi_wave_markup_behavior",
                "front_mid_rear_hierarchy_interaction",
                "leader_cycle_and_multi_leader_rotation",
                "catchup_order_and_secondary_diffusion",
                "high_level_consolidation_then_reacceleration",
                "post_regulation_decay_order_and_risk_monitoring",
                "concept_first_decay_vs structural_survivor_behavior",
                "cross_sector_resonance_and_fund_co_movement",
                "gem_or_st_liquidity_effect_on_high_level_stalls",
                "revival_after_deep_drawdown_and_future_known_catalyst_potential",
            ],
            "bounded_study_dimensions": [
                "three_wave_mainline_progression",
                "leader_vs_mid_core_vs_mapping_activation_role_drift",
                "catchup_timing_and extension_chain",
                "multi_subsector_inner_rotation",
                "regulatory_pause_and subsequent collapse ordering",
                "concept_decay_first_vs structural_anchor_persistence",
                "high_drawdown_abandonment_vs later_revival",
                "pre_visible_future_catalyst_as latent_reentry_driver",
            ],
            "immediate_deep_questions": [
                "Which internal roles survive across multiple waves rather than a single pulse?",
                "Which names are true commercial-space anchors versus story carriers with strong non-space absorption?",
                "How does post-regulation decay sequence differ between concept names and structural names?",
                "What explains later revivals after 30% to 50% drawdowns in previously abandoned names?",
            ],
        }

        candidate_rows = [
            {
                "symbol_or_name": "002085",
                "display_name": "\u4e07\u4e30\u5965\u5a01",
                "study_tier": "validated_local_seed",
                "current_reading": "clean_leader_seed",
            },
            {
                "symbol_or_name": "600118",
                "display_name": "\u4e2d\u56fd\u536b\u661f",
                "study_tier": "validated_local_seed",
                "current_reading": "policy_anchor_mid_core_seed",
            },
            {
                "symbol_or_name": "000738",
                "display_name": "\u822a\u53d1\u63a7\u5236",
                "study_tier": "validated_local_seed",
                "current_reading": "mapping_activation_seed_with_cross_theme_noise",
            },
            {
                "symbol_or_name": "\u822a\u5929\u53d1\u5c55",
                "display_name": "\u822a\u5929\u53d1\u5c55",
                "study_tier": "owner_named_candidate",
                "current_reading": "paradoxical_absorption_candidate",
            },
            {
                "symbol_or_name": "\u9c81\u4fe1\u521b\u6295",
                "display_name": "\u9c81\u4fe1\u521b\u6295",
                "study_tier": "owner_named_candidate",
                "current_reading": "concept_first_decay_candidate",
            },
            {
                "symbol_or_name": "\u822a\u5929\u5f69\u8679",
                "display_name": "\u822a\u5929\u5f69\u8679",
                "study_tier": "owner_named_candidate",
                "current_reading": "concept_first_decay_candidate",
            },
            {
                "symbol_or_name": "\u91d1\u98ce\u79d1\u6280",
                "display_name": "\u91d1\u98ce\u79d1\u6280",
                "study_tier": "owner_named_candidate",
                "current_reading": "cross_sector_resonance_candidate",
            },
            {
                "symbol_or_name": "ST\u94d6\u660c",
                "display_name": "ST\u94d6\u660c",
                "study_tier": "owner_named_candidate",
                "current_reading": "illiquidity_or_distribution_candidate",
            },
            {
                "symbol_or_name": "\u81fb\u96f7\u79d1\u6280",
                "display_name": "\u81fb\u96f7\u79d1\u6280",
                "study_tier": "owner_named_candidate",
                "current_reading": "gem_high_level_stall_candidate",
            },
            {
                "symbol_or_name": "\u5929\u94f6\u673a\u7535",
                "display_name": "\u5929\u94f6\u673a\u7535",
                "study_tier": "owner_named_candidate",
                "current_reading": "gem_revival_candidate",
            },
            {
                "symbol_or_name": "\u822a\u5929\u5b8f\u56fe",
                "display_name": "\u822a\u5929\u5b8f\u56fe",
                "study_tier": "owner_named_candidate",
                "current_reading": "name_association_early_extension_candidate",
            },
            {
                "symbol_or_name": "\u822a\u5b87\u5fae",
                "display_name": "\u822a\u5b87\u5fae",
                "study_tier": "owner_named_candidate",
                "current_reading": "name_association_early_extension_candidate",
            },
            {
                "symbol_or_name": "\u4e2d\u79d1\u661f\u56fe",
                "display_name": "\u4e2d\u79d1\u661f\u56fe",
                "study_tier": "owner_named_candidate",
                "current_reading": "direct_satellite_chain_candidate",
            },
            {
                "symbol_or_name": "\u4e7e\u7167\u5149\u7535",
                "display_name": "\u4e7e\u7167\u5149\u7535",
                "study_tier": "owner_named_candidate",
                "current_reading": "late_extension_and_deep_drawdown_candidate",
            },
            {
                "symbol_or_name": "\u987a\u707d\u80a1\u4efd",
                "display_name": "\u987a\u707d\u80a1\u4efd",
                "study_tier": "owner_named_candidate",
                "current_reading": "late_extension_candidate",
            },
            {
                "symbol_or_name": "\u5317\u6597\u661f\u901a",
                "display_name": "\u5317\u6597\u661f\u901a",
                "study_tier": "owner_named_candidate",
                "current_reading": "deep_drawdown_abandonment_candidate",
            },
            {
                "symbol_or_name": "\u4e09\u7ef4\u901a\u4fe1",
                "display_name": "\u4e09\u7ef4\u901a\u4fe1",
                "study_tier": "owner_named_candidate",
                "current_reading": "deep_drawdown_abandonment_candidate",
            },
            {
                "symbol_or_name": "\u518d\u5347\u79d1\u6280",
                "display_name": "\u518d\u5347\u79d1\u6280",
                "study_tier": "owner_named_candidate",
                "current_reading": "late_revival_candidate",
            },
            {
                "symbol_or_name": "\u897f\u90e8\u6d4b\u8bd5",
                "display_name": "\u897f\u90e8\u6d4b\u8bd5",
                "study_tier": "owner_named_candidate",
                "current_reading": "late_revival_candidate",
            },
        ]

        for row in candidate_rows:
            key = str(row["symbol_or_name"])
            row["validation_status"] = "locally_present" if key in validated_symbols else "owner_named_validation_pending"

        summary = {
            "acceptance_posture": "freeze_v113g_commercial_space_study_scope_v1",
            "selected_archetype": "commercial_space_mainline",
            "validated_local_seed_count": sum(1 for row in candidate_rows if row["study_tier"] == "validated_local_seed"),
            "owner_named_candidate_count": sum(1 for row in candidate_rows if row["study_tier"] == "owner_named_candidate"),
            "bounded_study_dimension_count": len(study_scope["bounded_study_dimensions"]),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "Commercial-space now exceeds a simple three-stock pilot correction problem and becomes a lawful deep-study archetype.",
            "The registry explicitly separates validated local seeds from broader owner-named candidates so the study can widen without pretending validation already exists.",
            "This phase still stops before label freeze or training; it only freezes why this archetype deserves deeper work and where that work should focus.",
        ]
        return V113GCommercialSpaceStudyScopeReport(
            summary=summary,
            study_scope=study_scope,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_v113g_commercial_space_study_scope_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113GCommercialSpaceStudyScopeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
