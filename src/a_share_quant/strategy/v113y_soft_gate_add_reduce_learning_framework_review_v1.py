from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113YSoftGateAddReduceLearningFrameworkReviewReport:
    summary: dict[str, Any]
    action_band_rows: list[dict[str, Any]]
    add_reduce_learning_rows: list[dict[str, Any]]
    reward_component_rows: list[dict[str, Any]]
    hard_veto_boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "action_band_rows": self.action_band_rows,
            "add_reduce_learning_rows": self.add_reduce_learning_rows,
            "reward_component_rows": self.reward_component_rows,
            "hard_veto_boundary_rows": self.hard_veto_boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113YSoftGateAddReduceLearningFrameworkReviewAnalyzer:
    def analyze(self, *, v113x_payload: dict[str, Any]) -> V113YSoftGateAddReduceLearningFrameworkReviewReport:
        summary_x = dict(v113x_payload.get("summary", {}))
        if str(summary_x.get("acceptance_posture")) != "freeze_v113x_probability_expectancy_sizing_framework_review_v1":
            raise ValueError("V1.13Y expects the V1.13X sizing framework review.")

        action_band_rows = [
            {
                "band_name": "hard_veto",
                "target_weight_band": [0.0, 0.0],
                "allowed_actions": ["close", "flat"],
                "reading": "This remains non-negotiable. The learning layer cannot talk its way out of a validated hard invalid-state trigger.",
            },
            {
                "band_name": "strong_de_risk",
                "target_weight_band": [0.05, 0.12],
                "allowed_actions": ["reduce"],
                "reading": "Used when expression should survive but needs a decisive cut rather than a token trim.",
            },
            {
                "band_name": "mild_de_risk",
                "target_weight_band": [0.10, 0.18],
                "allowed_actions": ["reduce", "hold"],
                "reading": "This is the main compromise layer between hard veto and overconfident hold.",
            },
            {
                "band_name": "probe_expression",
                "target_weight_band": [0.05, 0.10],
                "allowed_actions": ["open", "hold", "reduce"],
                "reading": "Designed for uncertain but still interesting states. It should exist as a real state, not collapse back into skip.",
            },
            {
                "band_name": "medium_expression",
                "target_weight_band": [0.12, 0.20],
                "allowed_actions": ["open", "add", "hold", "reduce"],
                "reading": "This is the default working band for good but not top-tier lines.",
            },
            {
                "band_name": "high_expression",
                "target_weight_band": [0.20, 0.30],
                "allowed_actions": ["open", "add", "hold", "reduce"],
                "reading": "Once the board is strong and the line is top-tier, the system should be allowed to press size instead of hiding in cash.",
            },
        ]

        add_reduce_learning_rows = [
            {
                "learning_problem": "add_when_correct",
                "state_question": "When should an existing valid position be increased instead of merely held?",
                "candidate_action_levels": ["hold", "add_to_medium", "add_to_high"],
                "reading": "The current stack knows how to open, but under-expresses during follow-through. Add-learning should close that gap first.",
            },
            {
                "learning_problem": "reduce_when_not_yet_veto",
                "state_question": "When should a still-valid line be trimmed without collapsing it to zero?",
                "candidate_action_levels": ["hold", "reduce_to_mild", "reduce_to_strong"],
                "reading": "This is the missing middle layer between being too brave and too binary.",
            },
            {
                "learning_problem": "re_add_after_repair",
                "state_question": "If a line was de-risked and quality repairs, can the system add back without waiting for a totally fresh re-entry story?",
                "candidate_action_levels": ["stay_mild", "re_add_to_medium", "re_add_to_high"],
                "reading": "Without re-add learning, the system will keep paying an over-caution tax even after it identifies recovery.",
            },
        ]

        reward_component_rows = [
            {
                "reward_component": "next_window_expectancy_capture",
                "weight_direction": "positive",
                "reading": "Reward the system when size is increased ahead of genuinely positive continuation windows.",
            },
            {
                "reward_component": "drawdown_penalty",
                "weight_direction": "negative",
                "reading": "Large losses still matter, but they should no longer dominate the objective so much that everything becomes underweight.",
            },
            {
                "reward_component": "under_exposure_penalty_on_confirmed_board_strength",
                "weight_direction": "negative",
                "reading": "This is the new missing cost. Staying too light on obvious strong-board days must become painful in the objective.",
            },
            {
                "reward_component": "over_trading_penalty",
                "weight_direction": "negative",
                "reading": "Add/reduce learning must not degenerate into noisy churn.",
            },
            {
                "reward_component": "holding_veto_override_respect",
                "weight_direction": "negative_if_violated",
                "reading": "The learning layer can explore within valid states, but it should be punished for fighting hard invalid-state controls.",
            },
        ]

        hard_veto_boundary_rows = [
            {
                "control_family": "holding_veto",
                "learning_role": "not_learned_only_respected",
                "reading": "Learning can decide size before the cliff, not whether the cliff exists.",
            },
            {
                "control_family": "entry_veto",
                "learning_role": "not_learned_only_respected",
                "reading": "Invalid entry states remain blocked. Soft-gating is for uncertainty, not for knowingly bad setups.",
            },
            {
                "control_family": "risk_off_override",
                "learning_role": "cap_layer",
                "reading": "Global risk-off can shrink all expressions, but should still sit above the learning layer as an emergency brake.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113y_soft_gate_add_reduce_learning_framework_review_v1",
            "core_posture": "hard_veto_plus_soft_sizing_with_add_reduce_learning",
            "binary_gate_replacement_ready": True,
            "learning_scope_first": "position_sizing_and_add_reduce_not_end_to_end_stock_picking",
            "reward_focus": "capture_expectancy_without_reverting_to_binary_timidity",
            "recommended_next_posture": "open_constrained_add_reduce_policy_search_protocol_before_full_rl",
        }
        interpretation = [
            "V1.13Y formalizes the compromise the current replay needs: keep hard vetoes, but replace most remaining binary gates with soft sizing bands.",
            "Add and reduce are promoted to first-class learning targets because the replay weakness is no longer pure entry logic; it is under-expression after being structurally correct.",
            "This keeps learning constrained and auditable: the system learns how much to express, not whether to ignore already-frozen invalid-state rules.",
        ]
        return V113YSoftGateAddReduceLearningFrameworkReviewReport(
            summary=summary,
            action_band_rows=action_band_rows,
            add_reduce_learning_rows=add_reduce_learning_rows,
            reward_component_rows=reward_component_rows,
            hard_veto_boundary_rows=hard_veto_boundary_rows,
            interpretation=interpretation,
        )


def write_v113y_soft_gate_add_reduce_learning_framework_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113YSoftGateAddReduceLearningFrameworkReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
