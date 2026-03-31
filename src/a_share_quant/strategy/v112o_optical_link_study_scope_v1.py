from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112OOpticalLinkStudyScopeReport:
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


class V112OOpticalLinkStudyScopeAnalyzer:
    """Freeze a bounded deep-study registry for the optical-link upcycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
    ) -> V112OOpticalLinkStudyScopeReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112o_now")):
            raise ValueError("V1.12O must be open before study-scope freeze.")

        dataset_rows = list(pilot_dataset_payload.get("dataset_rows", []))
        validated_symbols = {str(row.get("symbol", "")) for row in dataset_rows}

        study_scope = {
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "why_high_value_now": [
                "leader_vs_beta_divergence_across_multi_stage_markup",
                "module_core_vs_upstream_component_platform_split",
                "late_markup_vs_high_level_consolidation_semantic_divergence",
                "expectation_gap_reset_after_long_box",
                "cohort_breadth_confirmation_vs_isolated_hold",
                "cpo_adjacency_vs_core_optical_link_signal_purity",
                "earnings_transmission_carry_with_theme_overlap",
            ],
            "bounded_study_dimensions": [
                "core_module_leader_vs_high_beta_core_module",
                "upstream_component_platform_absorption",
                "adjacent_cohort_validation_before_training_widening",
                "late_cycle_persistence_vs_exhaustion_divergence",
                "cohort_breadth_confirmation_vs_single_name_hold",
                "cpo_adjacency_drift_and_signal_contamination",
                "profit_bridge_clarity_vs_thematic_story_leakage",
                "cycle_window_alignment_across_cohort_roles",
            ],
            "immediate_deep_questions": [
                "Which adjacent names are true optical-link earnings-transmission beneficiaries versus thematic spillovers?",
                "How far can the cohort widen before training grammar loses purity?",
                "Which roles deserve later bounded expansion beyond leader, high-beta core, and upstream component platform?",
                "Where does CPO adjacency start to add noise rather than useful transmission evidence?",
            ],
        }

        candidate_rows = [
            {
                "symbol_or_name": "300308",
                "display_name": "中际旭创",
                "study_tier": "validated_local_seed",
                "current_reading": "clean_leader_core_module_seed",
            },
            {
                "symbol_or_name": "300502",
                "display_name": "新易盛",
                "study_tier": "validated_local_seed",
                "current_reading": "high_beta_core_module_seed",
            },
            {
                "symbol_or_name": "300394",
                "display_name": "天孚通信",
                "study_tier": "validated_local_seed",
                "current_reading": "upstream_component_platform_seed",
            },
            {
                "symbol_or_name": "002281",
                "display_name": "光迅科技",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "legacy_domestic_optics_platform_candidate",
            },
            {
                "symbol_or_name": "603083",
                "display_name": "剑桥科技",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "high_beta_extension_candidate",
            },
            {
                "symbol_or_name": "688205",
                "display_name": "德科立",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "high_end_module_extension_candidate",
            },
            {
                "symbol_or_name": "301205",
                "display_name": "联特科技",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "smaller_cap_high_beta_candidate",
            },
            {
                "symbol_or_name": "300620",
                "display_name": "光库科技",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "upstream_photonics_cpo_adjacent_candidate",
            },
            {
                "symbol_or_name": "300548",
                "display_name": "博创科技",
                "study_tier": "review_only_adjacent_candidate",
                "current_reading": "module_and_cpo_adjacency_candidate",
            },
        ]

        for row in candidate_rows:
            key = str(row["symbol_or_name"])
            row["validation_status"] = "locally_present" if key in validated_symbols else "review_only_pending_validation"

        summary = {
            "acceptance_posture": "freeze_v112o_optical_link_study_scope_v1",
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "validated_local_seed_count": sum(1 for row in candidate_rows if row["study_tier"] == "validated_local_seed"),
            "review_only_adjacent_candidate_count": sum(
                1 for row in candidate_rows if row["study_tier"] == "review_only_adjacent_candidate"
            ),
            "bounded_study_dimension_count": len(study_scope["bounded_study_dimensions"]),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "Optical-link is no longer only a frozen three-symbol pilot; it now has an explicit deep-study registry.",
            "The adjacent names remain review-only candidates so the line can widen carefully without pretending they already belong in training.",
            "This scope keeps CPO as the current mainline without reopening the already-closed local refinement pocket.",
        ]
        return V112OOpticalLinkStudyScopeReport(
            summary=summary,
            study_scope=study_scope,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_v112o_optical_link_study_scope_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112OOpticalLinkStudyScopeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
