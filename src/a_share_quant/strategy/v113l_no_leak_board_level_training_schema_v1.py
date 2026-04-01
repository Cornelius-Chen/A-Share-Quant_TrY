from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113LNoLeakBoardLevelTrainingSchemaReport:
    summary: dict[str, Any]
    allowed_field_rows: list[dict[str, Any]]
    blocked_field_rows: list[dict[str, Any]]
    labeling_rule_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "allowed_field_rows": self.allowed_field_rows,
            "blocked_field_rows": self.blocked_field_rows,
            "labeling_rule_rows": self.labeling_rule_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113LNoLeakBoardLevelTrainingSchemaAnalyzer:
    def analyze(
        self,
        *,
        v113i_payload: dict[str, Any],
        v113j_payload: dict[str, Any],
        v113k_payload: dict[str, Any],
    ) -> V113LNoLeakBoardLevelTrainingSchemaReport:
        i_summary = dict(v113i_payload.get("summary", {}))
        j_summary = dict(v113j_payload.get("summary", {}))
        k_summary = dict(v113k_payload.get("summary", {}))

        if str(i_summary.get("acceptance_posture")) != "freeze_v113i_board_level_owner_labeling_protocol_v1":
            raise ValueError("V1.13L expects the board-level owner labeling protocol first.")
        if str(j_summary.get("acceptance_posture")) != "freeze_v113j_board_research_world_model_protocol_v1":
            raise ValueError("V1.13L expects the world-model protocol first.")
        if str(k_summary.get("acceptance_posture")) != "freeze_v113k_cpo_world_model_asset_mapping_v1":
            raise ValueError("V1.13L expects the first board world-model asset mapping first.")

        allowed_field_rows = [
            {
                "field_group": "board_state_inputs",
                "allowed_fields": [
                    "board_phase_label_owner",
                    "board_tradeability_label_owner",
                    "board_mainline_status_owner",
                    "breadth_snapshot",
                    "turnover_concentration_snapshot",
                    "leader_concentration_snapshot",
                    "board_relative_strength_snapshot",
                ],
                "reason": "Top-level board state and market-observable structure are point-in-time lawful.",
            },
            {
                "field_group": "world_model_priors",
                "allowed_fields": [
                    "object_presence_flags",
                    "relation_presence_flags",
                    "transition_template_ids",
                    "constraint_template_ids",
                ],
                "reason": "World-model priors teach mechanism grammar, not realized future outcomes.",
            },
            {
                "field_group": "fine_grained_internal_labels",
                "allowed_fields": [
                    "role_label_assistant",
                    "control_label_assistant",
                    "state_label_assistant",
                    "residual_family_label_assistant",
                    "assistant_confidence_tier",
                ],
                "reason": "Fine-grained labels are allowed only when derived from point-in-time structure and kept below owner board truth.",
            },
            {
                "field_group": "market_context_inputs",
                "allowed_fields": [
                    "market_regime_overlay",
                    "cross_board_resonance_snapshot",
                    "liquidity_snapshot",
                    "sentiment_proxy_snapshot",
                ],
                "reason": "Context inputs are lawful when sourced from same-day or prior observable market state.",
            },
        ]

        blocked_field_rows = [
            {
                "field_group": "future_outcomes",
                "blocked_fields": [
                    "forward_return_any_horizon",
                    "future_max_drawdown",
                    "future_peak_gain",
                    "future_trade_quality_label",
                ],
                "reason": "Direct future outcomes are target-side information and may not enter features.",
            },
            {
                "field_group": "post_cycle_truth",
                "blocked_fields": [
                    "final_promoted_status",
                    "final_mainline_winner_flag",
                    "final_leader_flag",
                    "full_cycle_realized_role",
                ],
                "reason": "Final cycle knowledge is exactly the hindsight leakage we must prevent.",
            },
            {
                "field_group": "direct_research_conclusions",
                "blocked_fields": [
                    "owner_after_the_fact_summary_text",
                    "manual_postmortem_conclusion_embedding",
                    "promotion_memo_result",
                    "phase_closure_result_flag",
                ],
                "reason": "Research conclusions may guide protocol design but cannot be injected as training answers.",
            },
            {
                "field_group": "diagnostic_and_sidecar_truth",
                "blocked_fields": [
                    "diagnostic_cluster_outputs_as_main_features",
                    "strong_derisk_sidecar_as_default_truth",
                    "review_only_labels_as_hard_truth",
                ],
                "reason": "Diagnostic, sidecar, and review-only objects are governance tools, not default main training truth.",
            },
        ]

        labeling_rule_rows = [
            {
                "rule_name": "cycle_split_only",
                "reading": "Train, validation, and test must be split by time or by whole cycle, never by random mixing.",
            },
            {
                "rule_name": "point_in_time_labeling",
                "reading": "All assistant fine-grained labels must be generated from information visible at or before the labeled date.",
            },
            {
                "rule_name": "owner_board_precedence",
                "reading": "Owner board-level labels are the top truth layer. Assistant labels refine internally but may not overrule board truth.",
            },
            {
                "rule_name": "sidecar_exclusion",
                "reading": "Sidecar and diagnostic structures may be logged for audit but cannot automatically enter the main training feature set.",
            },
            {
                "rule_name": "world_model_mechanism_only",
                "reading": "World-model tables may contribute objects, relations, transitions, and constraints, but not realized future answers.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113l_no_leak_board_level_training_schema_v1",
            "allowed_group_count": len(allowed_field_rows),
            "blocked_group_count": len(blocked_field_rows),
            "labeling_rule_count": len(labeling_rule_rows),
            "training_unit": "board_state_episode_with_cross_sectional_internal_points",
            "split_policy": "time_or_cycle_only",
            "recommended_next_posture": "build_board_level_training_tables_under_v113l_allow_block_schema",
        }
        interpretation = [
            "V1.13L converts the current board-labeling and world-model protocols into an explicit no-leak training schema.",
            "The schema allows mechanism priors and point-in-time board structure, but blocks all post-cycle truth and future outcome fields from feature space.",
            "This is the minimum governance layer needed before any real board-level training tables should be assembled.",
        ]
        return V113LNoLeakBoardLevelTrainingSchemaReport(
            summary=summary,
            allowed_field_rows=allowed_field_rows,
            blocked_field_rows=blocked_field_rows,
            labeling_rule_rows=labeling_rule_rows,
            interpretation=interpretation,
        )


def write_v113l_no_leak_board_level_training_schema_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113LNoLeakBoardLevelTrainingSchemaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
