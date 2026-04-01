from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113KCPOWorldModelAssetMappingReport:
    summary: dict[str, Any]
    object_rows: list[dict[str, Any]]
    relation_rows: list[dict[str, Any]]
    transition_rows: list[dict[str, Any]]
    constraint_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "object_rows": self.object_rows,
            "relation_rows": self.relation_rows,
            "transition_rows": self.transition_rows,
            "constraint_rows": self.constraint_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113KCPOWorldModelAssetMappingAnalyzer:
    def analyze(
        self,
        *,
        v113j_payload: dict[str, Any],
        v112cw_payload: dict[str, Any],
        v112cx_payload: dict[str, Any],
        v112cs_payload: dict[str, Any],
    ) -> V113KCPOWorldModelAssetMappingReport:
        j_summary = dict(v113j_payload.get("summary", {}))
        if str(j_summary.get("acceptance_posture")) != "freeze_v113j_board_research_world_model_protocol_v1":
            raise ValueError("V1.13K expects V1.13J world-model protocol freeze first.")

        cw_rows = list(v112cw_payload.get("stack_rows", []))
        cx_rows = list(v112cx_payload.get("promotion_rows", []))
        cs_rows = list(v112cs_payload.get("stack_rows", []))

        packaging_mainline = next(row for row in cw_rows if str(row.get("stack_item")) == "packaging_process_enabler")
        packaging_extension = next(row for row in cw_rows if str(row.get("stack_item")) == "packaging_admission_extension")
        core_leader = next(row for row in cs_rows if str(row.get("stack_item")) == "300308_core_module_leader")
        high_beta_core = next(row for row in cs_rows if str(row.get("stack_item")) == "300502_high_beta_core_module")
        laser = next(row for row in cs_rows if str(row.get("stack_item")) == "laser_chip_component")
        core_leader_rule = cx_rows[0]

        object_rows = [
            {
                "object_id": "cpo_theme_board",
                "object_type": "theme_board",
                "status": "active_world_model_anchor",
                "description": "CPO board under study with frozen packaging mainline surface and controlled residual stack.",
            },
            {
                "object_id": "packaging_process_enabler",
                "object_type": "role_family",
                "status": packaging_mainline.get("status"),
                "control_language": packaging_mainline.get("control_language"),
            },
            {
                "object_id": "packaging_admission_extension",
                "object_type": "admission_extension",
                "status": packaging_extension.get("status"),
                "control_language": packaging_extension.get("control_language"),
            },
            {
                "object_id": "core_module_leader",
                "object_type": "role_family",
                "status": core_leader.get("status"),
                "control_language": core_leader.get("control_language"),
            },
            {
                "object_id": "high_beta_core_module",
                "object_type": "role_family",
                "status": high_beta_core.get("status"),
                "control_language": high_beta_core.get("control_language"),
            },
            {
                "object_id": "laser_chip_component",
                "object_type": "role_family",
                "status": laser.get("status"),
                "control_language": laser.get("control_language"),
            },
        ]

        relation_rows = [
            {
                "relation_id": "packaging_belongs_to_cpo_mainline_surface",
                "source_object": "packaging_process_enabler",
                "target_object": "cpo_theme_board",
                "relation_type": "mainline_surface_member",
            },
            {
                "relation_id": "packaging_admission_extends_packaging_surface",
                "source_object": "packaging_admission_extension",
                "target_object": "packaging_process_enabler",
                "relation_type": "admission_extension_of",
            },
            {
                "relation_id": "core_leader_outside_packaging_surface",
                "source_object": "core_module_leader",
                "target_object": "packaging_process_enabler",
                "relation_type": "separate_residual_control",
            },
            {
                "relation_id": "high_beta_core_sidecar_to_core_stack",
                "source_object": "high_beta_core_module",
                "target_object": "core_module_leader",
                "relation_type": "sidecar_to_residual_stack",
            },
            {
                "relation_id": "laser_member_of_template_capable_cluster",
                "source_object": "laser_chip_component",
                "target_object": "packaging_process_enabler",
                "relation_type": "eligibility_only_cluster_member",
            },
        ]

        transition_rows = [
            {
                "transition_id": "packaging_eligibility_to_admission_extension",
                "from_state": "miss_while_cash",
                "to_state": "controlled_mainline_extension",
                "anchor_object": "packaging_admission_extension",
            },
            {
                "transition_id": "core_leader_continue_to_holding_veto",
                "from_state": "continue",
                "to_state": "holding_veto",
                "anchor_object": "core_module_leader",
                "trigger_rule": core_leader_rule.get("selected_rule_name"),
            },
            {
                "transition_id": "high_beta_core_eligibility_to_mild_derisk",
                "from_state": "eligibility",
                "to_state": "neutral_safe_mild_derisk",
                "anchor_object": "high_beta_core_module",
            },
            {
                "transition_id": "laser_eligibility_to_fringe_watch",
                "from_state": "eligibility",
                "to_state": "fringe_watch",
                "anchor_object": "laser_chip_component",
            },
        ]

        constraint_rows = [
            {
                "constraint_id": "packaging_learning_frozen",
                "constraint_type": "learning_boundary",
                "reading": "Packaging template learning is frozen; only governed extension replay may be added.",
            },
            {
                "constraint_id": "joint_core_promotion_deferred",
                "constraint_type": "promotion_boundary",
                "reading": "300308 and 300502 cannot be jointly promoted into a unified core stack at the current stage.",
            },
            {
                "constraint_id": "high_beta_core_strong_derisk_not_default",
                "constraint_type": "sidecar_boundary",
                "reading": "Evidence-optimizing stronger de-risk for 300502 may not replace the neutral-safe mild band as default behavior.",
            },
            {
                "constraint_id": "laser_not_three_layer",
                "constraint_type": "template_boundary",
                "reading": "Laser-chip may not inherit packaging's full three-layer action language.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113k_cpo_world_model_asset_mapping_v1",
            "board_name": "CPO",
            "object_count": len(object_rows),
            "relation_count": len(relation_rows),
            "transition_count": len(transition_rows),
            "constraint_count": len(constraint_rows),
            "recommended_next_posture": "reuse_v113k_mapping_as_board_world_model_seed_for_future_board_level_training_and_execution_priors",
        }
        interpretation = [
            "V1.13K maps the current frozen CPO assets into the four-layer world-model structure defined by V1.13J.",
            "The output is not a signal sheet; it is a reusable world-model seed containing entities, links, transitions, and hard boundaries.",
            "This gives future board-level training a mechanism prior instead of forcing it to memorize single-cycle answers.",
        ]
        return V113KCPOWorldModelAssetMappingReport(
            summary=summary,
            object_rows=object_rows,
            relation_rows=relation_rows,
            transition_rows=transition_rows,
            constraint_rows=constraint_rows,
            interpretation=interpretation,
        )


def write_v113k_cpo_world_model_asset_mapping_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113KCPOWorldModelAssetMappingReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
