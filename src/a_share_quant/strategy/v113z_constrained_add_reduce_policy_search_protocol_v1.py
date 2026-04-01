from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113ZConstrainedAddReducePolicySearchProtocolReport:
    summary: dict[str, Any]
    search_space_rows: list[dict[str, Any]]
    state_input_rows: list[dict[str, Any]]
    reward_rows: list[dict[str, Any]]
    validation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "search_space_rows": self.search_space_rows,
            "state_input_rows": self.state_input_rows,
            "reward_rows": self.reward_rows,
            "validation_rows": self.validation_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113ZConstrainedAddReducePolicySearchProtocolAnalyzer:
    def analyze(
        self,
        *,
        v113v_payload: dict[str, Any],
        v113x_payload: dict[str, Any],
        v113y_payload: dict[str, Any],
    ) -> V113ZConstrainedAddReducePolicySearchProtocolReport:
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_x = dict(v113x_payload.get("summary", {}))
        summary_y = dict(v113y_payload.get("summary", {}))
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.13Z expects the V1.13V replay report.")
        if str(summary_x.get("acceptance_posture")) != "freeze_v113x_probability_expectancy_sizing_framework_review_v1":
            raise ValueError("V1.13Z expects the V1.13X sizing framework review.")
        if str(summary_y.get("acceptance_posture")) != "freeze_v113y_soft_gate_add_reduce_learning_framework_review_v1":
            raise ValueError("V1.13Z expects the V1.13Y soft-gate learning framework review.")

        search_space_rows = [
            {
                "action_family": "entry_expression",
                "allowed_action_levels": ["skip", "probe_expression", "medium_expression", "high_expression"],
                "weight_grid": [0.00, 0.06, 0.10, 0.14, 0.18, 0.22, 0.26, 0.30],
                "reading": "Search stays on a discrete grid so that policy learning remains auditable and does not hide behind tiny continuous adjustments.",
            },
            {
                "action_family": "add_expression",
                "allowed_action_levels": ["hold", "add_to_medium", "add_to_high"],
                "weight_grid": [0.00, 0.04, 0.08, 0.12],
                "reading": "Adds are only allowed to lift an existing position from a lower valid band to a higher valid band.",
            },
            {
                "action_family": "reduce_expression",
                "allowed_action_levels": ["hold", "reduce_to_mild", "reduce_to_strong"],
                "weight_grid": [0.00, -0.04, -0.08, -0.12],
                "reading": "Reduce learning is explicitly non-binary. The search should learn trims before it learns exits.",
            },
            {
                "action_family": "hard_invalid_state",
                "allowed_action_levels": ["force_exit"],
                "weight_grid": [0.00],
                "reading": "Hard veto remains outside the learning search. The protocol searches soft expression, not whether to ignore invalid states.",
            },
        ]

        state_input_rows = [
            {
                "input_family": "board_strength_context",
                "fields": ["board_avg_return", "board_breadth", "top3_turnover_ratio"],
                "role": "board_state_strength",
            },
            {
                "input_family": "source_semantics",
                "fields": ["source_family", "probability_band", "default_expression"],
                "role": "structural_prior",
            },
            {
                "input_family": "account_expression_state",
                "fields": ["gross_exposure_after_close", "symbol_weight", "cash_weight"],
                "role": "current_capital_deployment",
            },
            {
                "input_family": "position_transition_state",
                "fields": ["is_new_entry", "has_existing_position", "is_derisk_state", "is_holding_veto_state"],
                "role": "action_context",
            },
            {
                "input_family": "board_episode_quality",
                "fields": ["episode_count", "planned_order_count", "sizing_reading"],
                "role": "local_action_quality_proxy",
            },
        ]

        reward_rows = [
            {
                "reward_component": "next_window_return_capture",
                "formula_role": "positive",
                "reading": "The policy should be rewarded for increasing size when future continuation actually pays.",
            },
            {
                "reward_component": "under_exposure_penalty",
                "formula_role": "negative",
                "reading": "Strong-board days with weak gross exposure must be penalized directly; otherwise the learner will rediscover timidity.",
            },
            {
                "reward_component": "drawdown_penalty",
                "formula_role": "negative",
                "reading": "Drawdown still matters, but as one term among several rather than the only thing the system fears.",
            },
            {
                "reward_component": "turnover_penalty",
                "formula_role": "negative",
                "reading": "This prevents the learner from gaming the reward through noisy add/reduce churn.",
            },
            {
                "reward_component": "hard_veto_violation_penalty",
                "formula_role": "large_negative",
                "reading": "The search should not earn freedom by breaking already-validated hard invalid-state rules.",
            },
            {
                "reward_component": "cash_drag_penalty_on_confirmed_high_expression",
                "formula_role": "negative",
                "reading": "This captures the exact failure the replay exposed: staying too light even when the board and source semantics already justify size.",
            },
        ]

        validation_rows = [
            {
                "validation_rule": "walk_forward_only",
                "reading": "Search parameters must be fitted on earlier windows and scored on later windows only.",
            },
            {
                "validation_rule": "cycle_split_preferred_over_random_split",
                "reading": "The protocol must not mix the same board cycle across train and test in order to avoid path memorization.",
            },
            {
                "validation_rule": "selection_logic_frozen_during_sizing_search",
                "reading": "This search is not allowed to rewrite stock selection or hard-veto logic while tuning position expression.",
            },
            {
                "validation_rule": "policy_must_beat_current_replay_on_risk_adjusted_basis",
                "reading": "Promotion should require better expression efficiency without surrendering the current drawdown discipline.",
            },
            {
                "validation_rule": "audit_log_required",
                "reading": "Every learned action must be reconstructible as state -> action-band -> target-weight, not just as an opaque score.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113z_constrained_add_reduce_policy_search_protocol_v1",
            "search_scope": "constrained_position_expression_only",
            "selection_logic_rewrite_allowed": False,
            "hard_veto_override_allowed": False,
            "walk_forward_required": True,
            "cycle_split_required": True,
            "ready_for_policy_search_pilot_next": True,
            "recommended_next_posture": "run_first_constrained_add_reduce_policy_search_pilot_on_cpo_replay",
        }
        interpretation = [
            "V1.13Z turns the current sizing discussion into a concrete search protocol instead of letting the project drift into unconstrained random exploration.",
            "The learner is allowed to search expression bands and add/reduce moves, but it is not allowed to rewrite validated selection or hard-veto semantics.",
            "This preserves the current research assets while opening a legitimate path toward self-improving sizing behaviour.",
        ]
        return V113ZConstrainedAddReducePolicySearchProtocolReport(
            summary=summary,
            search_space_rows=search_space_rows,
            state_input_rows=state_input_rows,
            reward_rows=reward_rows,
            validation_rows=validation_rows,
            interpretation=interpretation,
        )


def write_v113z_constrained_add_reduce_policy_search_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113ZConstrainedAddReducePolicySearchProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
