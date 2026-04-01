from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113MBoardLevelTrainingTableAssemblyReport:
    summary: dict[str, Any]
    table_rows: list[dict[str, Any]]
    field_rows: list[dict[str, Any]]
    sample_episode_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "table_rows": self.table_rows,
            "field_rows": self.field_rows,
            "sample_episode_rows": self.sample_episode_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113MBoardLevelTrainingTableAssemblyAnalyzer:
    def analyze(
        self,
        *,
        v113i_payload: dict[str, Any],
        v113k_payload: dict[str, Any],
        v113l_payload: dict[str, Any],
    ) -> V113MBoardLevelTrainingTableAssemblyReport:
        i_summary = dict(v113i_payload.get("summary", {}))
        k_summary = dict(v113k_payload.get("summary", {}))
        l_summary = dict(v113l_payload.get("summary", {}))

        if str(i_summary.get("acceptance_posture")) != "freeze_v113i_board_level_owner_labeling_protocol_v1":
            raise ValueError("V1.13M expects the V1.13I owner-labeling protocol first.")
        if str(k_summary.get("acceptance_posture")) != "freeze_v113k_cpo_world_model_asset_mapping_v1":
            raise ValueError("V1.13M expects the V1.13K CPO world-model mapping first.")
        if str(l_summary.get("acceptance_posture")) != "freeze_v113l_no_leak_board_level_training_schema_v1":
            raise ValueError("V1.13M expects the V1.13L no-leak training schema first.")

        object_rows = list(v113k_payload.get("object_rows", []))
        relation_rows = list(v113k_payload.get("relation_rows", []))
        transition_rows = list(v113k_payload.get("transition_rows", []))
        constraint_rows = list(v113k_payload.get("constraint_rows", []))
        allowed_field_rows = list(v113l_payload.get("allowed_field_rows", []))
        blocked_field_rows = list(v113l_payload.get("blocked_field_rows", []))

        board_name = str(k_summary.get("board_name", "UNKNOWN"))

        table_rows = [
            {
                "table_name": "board_state_episode_table",
                "primary_key": "episode_id",
                "grain": "board_date_episode",
                "role": "Top-level training table holding owner board labels, point-in-time context, and aggregated internal structure.",
            },
            {
                "table_name": "board_cross_section_internal_point_table",
                "primary_key": "episode_point_id",
                "grain": "board_date_object_point",
                "role": "Assistant fine-grained labels for role families and residual control objects under the same board episode.",
            },
            {
                "table_name": "board_world_model_prior_table",
                "primary_key": "world_model_prior_id",
                "grain": "board_mechanism_prior_snapshot",
                "role": "Mechanism priors from objects, relations, transitions, and constraints. Priors teach grammar, not future answers.",
            },
        ]

        field_rows = [
            {
                "table_name": "board_state_episode_table",
                "field_group": "owner_truth",
                "fields": [
                    "episode_id",
                    "board_name",
                    "board_phase_label_owner",
                    "board_tradeability_label_owner",
                    "board_mainline_status_owner",
                ],
            },
            {
                "table_name": "board_state_episode_table",
                "field_group": "market_context",
                "fields": [
                    "breadth_snapshot",
                    "turnover_concentration_snapshot",
                    "leader_concentration_snapshot",
                    "board_relative_strength_snapshot",
                    "market_regime_overlay",
                    "cross_board_resonance_snapshot",
                    "liquidity_snapshot",
                    "sentiment_proxy_snapshot",
                ],
            },
            {
                "table_name": "board_cross_section_internal_point_table",
                "field_group": "assistant_internal_grammar",
                "fields": [
                    "episode_point_id",
                    "episode_id",
                    "object_id",
                    "object_type",
                    "role_label_assistant",
                    "control_label_assistant",
                    "state_label_assistant",
                    "residual_family_label_assistant",
                    "assistant_confidence_tier",
                ],
            },
            {
                "table_name": "board_world_model_prior_table",
                "field_group": "mechanism_prior",
                "fields": [
                    "world_model_prior_id",
                    "episode_id",
                    "object_presence_flags",
                    "relation_presence_flags",
                    "transition_template_ids",
                    "constraint_template_ids",
                ],
            },
            {
                "table_name": "blocked_fields_registry",
                "field_group": "explicitly_blocked",
                "fields": [row.get("field_group") for row in blocked_field_rows],
            },
        ]

        relation_ids = [str(row.get("relation_id")) for row in relation_rows]
        transition_ids = [str(row.get("transition_id")) for row in transition_rows]
        constraint_ids = [str(row.get("constraint_id")) for row in constraint_rows]

        object_lookup = {str(row.get("object_id")): row for row in object_rows}

        sample_episode_rows = [
            {
                "episode_id": "cpo_main_markup_packaging_surface",
                "board_name": board_name,
                "board_phase_label_owner": "main_markup",
                "board_tradeability_label_owner": "tradable",
                "board_mainline_status_owner": "mainline",
                "object_id": "packaging_process_enabler",
                "object_type": object_lookup["packaging_process_enabler"]["object_type"],
                "role_label_assistant": "core",
                "control_label_assistant": "eligibility",
                "state_label_assistant": "mainline_surface_active",
                "residual_family_label_assistant": None,
                "assistant_confidence_tier": "hard",
                "object_presence_flags": [
                    "packaging_process_enabler",
                    "core_module_leader",
                    "high_beta_core_module",
                ],
                "relation_presence_flags": relation_ids[:2],
                "transition_template_ids": ["packaging_eligibility_to_admission_extension"],
                "constraint_template_ids": ["packaging_learning_frozen"],
            },
            {
                "episode_id": "cpo_main_markup_packaging_admission",
                "board_name": board_name,
                "board_phase_label_owner": "main_markup",
                "board_tradeability_label_owner": "tradable",
                "board_mainline_status_owner": "mainline",
                "object_id": "packaging_admission_extension",
                "object_type": object_lookup["packaging_admission_extension"]["object_type"],
                "role_label_assistant": "sidecar",
                "control_label_assistant": "admission_extension",
                "state_label_assistant": "miss_while_cash_recoverable",
                "residual_family_label_assistant": "eligibility_miss",
                "assistant_confidence_tier": "guarded",
                "object_presence_flags": [
                    "packaging_process_enabler",
                    "packaging_admission_extension",
                ],
                "relation_presence_flags": relation_ids[:2],
                "transition_template_ids": ["packaging_eligibility_to_admission_extension"],
                "constraint_template_ids": ["packaging_learning_frozen"],
            },
            {
                "episode_id": "cpo_main_markup_core_leader_hold_state",
                "board_name": board_name,
                "board_phase_label_owner": "main_markup",
                "board_tradeability_label_owner": "guarded",
                "board_mainline_status_owner": "mainline",
                "object_id": "core_module_leader",
                "object_type": object_lookup["core_module_leader"]["object_type"],
                "role_label_assistant": "leader",
                "control_label_assistant": "holding_veto",
                "state_label_assistant": "late_main_markup_overstay_risk",
                "residual_family_label_assistant": "overstay",
                "assistant_confidence_tier": "guarded",
                "object_presence_flags": [
                    "core_module_leader",
                    "high_beta_core_module",
                ],
                "relation_presence_flags": ["core_leader_outside_packaging_surface"],
                "transition_template_ids": ["core_leader_continue_to_holding_veto"],
                "constraint_template_ids": ["joint_core_promotion_deferred"],
            },
            {
                "episode_id": "cpo_diffusion_high_beta_core_expression",
                "board_name": board_name,
                "board_phase_label_owner": "diffusion",
                "board_tradeability_label_owner": "guarded",
                "board_mainline_status_owner": "mainline",
                "object_id": "high_beta_core_module",
                "object_type": object_lookup["high_beta_core_module"]["object_type"],
                "role_label_assistant": "core",
                "control_label_assistant": "de_risk",
                "state_label_assistant": "neutral_safe_mild_derisk_band",
                "residual_family_label_assistant": "expression_risk",
                "assistant_confidence_tier": "guarded",
                "object_presence_flags": [
                    "core_module_leader",
                    "high_beta_core_module",
                ],
                "relation_presence_flags": ["high_beta_core_sidecar_to_core_stack"],
                "transition_template_ids": ["high_beta_core_eligibility_to_mild_derisk"],
                "constraint_template_ids": [
                    "joint_core_promotion_deferred",
                    "high_beta_core_strong_derisk_not_default",
                ],
            },
            {
                "episode_id": "cpo_diffusion_laser_fringe_watch",
                "board_name": board_name,
                "board_phase_label_owner": "diffusion",
                "board_tradeability_label_owner": "guarded",
                "board_mainline_status_owner": "mainline",
                "object_id": "laser_chip_component",
                "object_type": object_lookup["laser_chip_component"]["object_type"],
                "role_label_assistant": "sidecar",
                "control_label_assistant": "eligibility",
                "state_label_assistant": "fringe_watch",
                "residual_family_label_assistant": None,
                "assistant_confidence_tier": "review_only",
                "object_presence_flags": [
                    "laser_chip_component",
                    "packaging_process_enabler",
                ],
                "relation_presence_flags": ["laser_member_of_template_capable_cluster"],
                "transition_template_ids": ["laser_eligibility_to_fringe_watch"],
                "constraint_template_ids": ["laser_not_three_layer"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113m_board_level_training_table_assembly_v1",
            "board_name": board_name,
            "table_count": len(table_rows),
            "field_group_count": len(field_rows),
            "sample_episode_count": len(sample_episode_rows),
            "training_unit": str(l_summary.get("training_unit")),
            "split_policy": str(l_summary.get("split_policy")),
            "allowed_field_group_count": len(allowed_field_rows),
            "blocked_field_group_count": len(blocked_field_rows),
            "recommended_next_posture": "build_real_board_level_episode_tables_from_owner_labels_and_point_in_time_market_snapshots_only",
        }
        interpretation = [
            "V1.13M is the first concrete assembly of a board-level training table, rather than another protocol-only freeze.",
            "The assembly preserves the V1.13L no-leak boundary by using board truth, internal grammar, and world-model priors only as point-in-time fields.",
            "The sample rows are not hindsight targets; they are lawful episode templates showing how CPO board states can be serialized into trainable records.",
        ]
        return V113MBoardLevelTrainingTableAssemblyReport(
            summary=summary,
            table_rows=table_rows,
            field_rows=field_rows,
            sample_episode_rows=sample_episode_rows,
            interpretation=interpretation,
        )


def write_v113m_board_level_training_table_assembly_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113MBoardLevelTrainingTableAssemblyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
