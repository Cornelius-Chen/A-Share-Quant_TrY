from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113NCPORealBoardEpisodePopulationReport:
    summary: dict[str, Any]
    board_episode_rows: list[dict[str, Any]]
    internal_point_rows: list[dict[str, Any]]
    world_model_prior_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "board_episode_rows": self.board_episode_rows,
            "internal_point_rows": self.internal_point_rows,
            "world_model_prior_rows": self.world_model_prior_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113NCPORealBoardEpisodePopulationAnalyzer:
    def analyze(
        self,
        *,
        v113m_payload: dict[str, Any],
        v112ct_payload: dict[str, Any],
        v112cn_payload: dict[str, Any],
        v112co_payload: dict[str, Any],
        v112ci_payload: dict[str, Any],
    ) -> V113NCPORealBoardEpisodePopulationReport:
        m_summary = dict(v113m_payload.get("summary", {}))
        if str(m_summary.get("acceptance_posture")) != "freeze_v113m_board_level_training_table_assembly_v1":
            raise ValueError("V1.13N expects the V1.13M training-table assembly first.")

        board_name = str(m_summary.get("board_name", "CPO"))

        packaging_rows = [
            {
                "trade_date": str(row["trade_date"]),
                "board_phase_label_owner": "main_markup",
                "board_tradeability_label_owner": "tradable",
                "board_mainline_status_owner": "mainline",
                "object_id": "packaging_process_enabler",
                "object_type": "role_family",
                "role_label_assistant": "core",
                "control_label_assistant": "eligibility",
                "state_label_assistant": "mainline_surface_active",
                "residual_family_label_assistant": None,
                "assistant_confidence_tier": "hard",
                "source_report": "v112ct",
            }
            for row in list(v112ct_payload.get("admission_rows", []))
            if str(row.get("mode_name")) == "full_20d_admission"
        ]

        core_leader_rows = [
            {
                "trade_date": str(row["entry_date"]),
                "board_phase_label_owner": "main_markup",
                "board_tradeability_label_owner": "guarded"
                if str(row.get("control_band")) == "holding_veto_band"
                else "tradable",
                "board_mainline_status_owner": "mainline",
                "object_id": "core_module_leader",
                "object_type": "role_family",
                "role_label_assistant": "leader",
                "control_label_assistant": "holding_veto"
                if str(row.get("control_band")) == "holding_veto_band"
                else "eligibility",
                "state_label_assistant": "late_main_markup_overstay_risk"
                if str(row.get("control_band")) == "holding_veto_band"
                else "hold_valid_under_current_state_band",
                "residual_family_label_assistant": "overstay"
                if str(row.get("control_band")) == "holding_veto_band"
                else None,
                "assistant_confidence_tier": "guarded"
                if str(row.get("control_band")) == "holding_veto_band"
                else "hard",
                "source_report": "v112cn",
            }
            for row in list(v112cn_payload.get("trade_band_rows", []))
        ]

        high_beta_rows = [
            {
                "trade_date": str(row["entry_date"]),
                "board_phase_label_owner": str(row.get("stage_family")),
                "board_tradeability_label_owner": "guarded"
                if str(row.get("control_band")) == "de_risk_band"
                else "tradable",
                "board_mainline_status_owner": "mainline",
                "object_id": "high_beta_core_module",
                "object_type": "role_family",
                "role_label_assistant": "core",
                "control_label_assistant": "de_risk"
                if str(row.get("control_band")) == "de_risk_band"
                else "eligibility",
                "state_label_assistant": "neutral_safe_mild_derisk_band"
                if str(row.get("control_band")) == "de_risk_band"
                else "expression_stays_eligible_under_current_state_band",
                "residual_family_label_assistant": "expression_risk"
                if str(row.get("control_band")) == "de_risk_band"
                else None,
                "assistant_confidence_tier": "guarded"
                if str(row.get("control_band")) == "de_risk_band"
                else "hard",
                "source_report": "v112co",
            }
            for row in list(v112co_payload.get("evidence_band_rows", []))
        ]

        laser_rows = [
            {
                "trade_date": str(row["trade_date"]),
                "board_phase_label_owner": "diffusion",
                "board_tradeability_label_owner": "guarded",
                "board_mainline_status_owner": "mainline",
                "object_id": "laser_chip_component",
                "object_type": "role_family",
                "role_label_assistant": "sidecar",
                "control_label_assistant": "eligibility",
                "state_label_assistant": str(row.get("maturation_reading")),
                "residual_family_label_assistant": None,
                "assistant_confidence_tier": "review_only"
                if str(row.get("maturation_reading")) == "de_risk_fringe_watch"
                else "guarded",
                "source_report": "v112ci",
            }
            for row in list(v112ci_payload.get("sample_rows", []))
        ]

        internal_point_rows = packaging_rows + core_leader_rows + high_beta_rows + laser_rows

        board_episode_rows: list[dict[str, Any]] = []
        seen_dates: set[tuple[str, str]] = set()
        for row in internal_point_rows:
            key = (str(row["trade_date"]), str(row["board_phase_label_owner"]))
            if key in seen_dates:
                continue
            seen_dates.add(key)
            board_episode_rows.append(
                {
                    "episode_id": f"{board_name.lower()}_{row['trade_date']}_{row['board_phase_label_owner']}",
                    "trade_date": row["trade_date"],
                    "board_name": board_name,
                    "board_phase_label_owner": row["board_phase_label_owner"],
                    "board_tradeability_label_owner": row["board_tradeability_label_owner"],
                    "board_mainline_status_owner": row["board_mainline_status_owner"],
                }
            )
        board_episode_rows = sorted(
            board_episode_rows,
            key=lambda row: (
                str(row["trade_date"]),
                str(row["board_phase_label_owner"]),
                str(row["episode_id"]),
            ),
        )

        world_model_prior_rows = []
        for row in internal_point_rows:
            object_id = str(row["object_id"])
            if object_id == "packaging_process_enabler":
                relation_flags = [
                    "packaging_belongs_to_cpo_mainline_surface",
                    "packaging_admission_extends_packaging_surface",
                ]
                transition_ids = ["packaging_eligibility_to_admission_extension"]
                constraint_ids = ["packaging_learning_frozen"]
            elif object_id == "core_module_leader":
                relation_flags = ["core_leader_outside_packaging_surface"]
                transition_ids = ["core_leader_continue_to_holding_veto"]
                constraint_ids = ["joint_core_promotion_deferred"]
            elif object_id == "high_beta_core_module":
                relation_flags = ["high_beta_core_sidecar_to_core_stack"]
                transition_ids = ["high_beta_core_eligibility_to_mild_derisk"]
                constraint_ids = [
                    "joint_core_promotion_deferred",
                    "high_beta_core_strong_derisk_not_default",
                ]
            else:
                relation_flags = ["laser_member_of_template_capable_cluster"]
                transition_ids = ["laser_eligibility_to_fringe_watch"]
                constraint_ids = ["laser_not_three_layer"]

            world_model_prior_rows.append(
                {
                    "world_model_prior_id": f"{board_name.lower()}_{row['trade_date']}_{object_id}_prior",
                    "trade_date": row["trade_date"],
                    "board_name": board_name,
                    "object_id": object_id,
                    "object_presence_flags": [object_id],
                    "relation_presence_flags": relation_flags,
                    "transition_template_ids": transition_ids,
                    "constraint_template_ids": constraint_ids,
                }
            )

        internal_point_rows = sorted(
            internal_point_rows,
            key=lambda row: (
                str(row["trade_date"]),
                str(row["object_id"]),
                str(row["control_label_assistant"]),
            ),
        )
        world_model_prior_rows = sorted(
            world_model_prior_rows,
            key=lambda row: (
                str(row["trade_date"]),
                str(row["object_id"]),
                str(row["world_model_prior_id"]),
            ),
        )

        summary = {
            "acceptance_posture": "freeze_v113n_cpo_real_board_episode_population_v1",
            "board_name": board_name,
            "board_episode_count": len(board_episode_rows),
            "internal_point_count": len(internal_point_rows),
            "world_model_prior_count": len(world_model_prior_rows),
            "packaging_row_count": len(packaging_rows),
            "core_leader_row_count": len(core_leader_rows),
            "high_beta_core_row_count": len(high_beta_rows),
            "laser_row_count": len(laser_rows),
            "recommended_next_posture": "use_v113n_real_cpo_episode_rows_as_first_board_level_training_seed_and_only_expand_with_point_in_time lawful rows",
        }
        interpretation = [
            "V1.13N upgrades the V1.13M sample schema into real dated CPO episode rows sourced from already frozen lawful control assets.",
            "The populated rows still obey the no-leak boundary: they serialize board truth, internal grammar, and world-model priors, but do not inject future returns into feature space.",
            "This is the first usable board-level training seed with actual trade dates rather than abstract placeholders.",
        ]
        return V113NCPORealBoardEpisodePopulationReport(
            summary=summary,
            board_episode_rows=board_episode_rows,
            internal_point_rows=internal_point_rows,
            world_model_prior_rows=world_model_prior_rows,
            interpretation=interpretation,
        )


def write_v113n_cpo_real_board_episode_population_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113NCPORealBoardEpisodePopulationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
