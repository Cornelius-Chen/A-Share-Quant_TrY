from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BCCPOPortfolioObjectiveProtocolReport:
    summary: dict[str, Any]
    objective_track_rows: list[dict[str, Any]]
    model_scope_rows: list[dict[str, Any]]
    evaluation_metric_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "objective_track_rows": self.objective_track_rows,
            "model_scope_rows": self.model_scope_rows,
            "evaluation_metric_rows": self.evaluation_metric_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BCCPOPortfolioObjectiveProtocolAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        v112bb_pilot_payload: dict[str, Any],
        v112z_operational_charter_payload: dict[str, Any],
    ) -> V112BCCPOPortfolioObjectiveProtocolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112bc_now")):
            raise ValueError("V1.12BC must be open before protocol freeze.")

        default_pilot_summary = dict(v112bb_pilot_payload.get("summary", {}))
        if not bool(default_pilot_summary.get("default_10_row_pilot_established")):
            raise ValueError("V1.12BC requires the default 10-row bounded pilot baseline from V1.12BB.")

        operational_summary = dict(v112z_operational_charter_payload.get("summary", {}))
        if str(operational_summary.get("black_box_primary_family")) != "hist_gradient_boosting_classifier":
            raise ValueError("V1.12BC expects the current primary black-box model posture from V1.12Z.")

        objective_track_rows = [
            {
                "track_name": "oracle_upper_bound_track",
                "track_posture": "hindsight_benchmark_only",
                "future_information_allowed": True,
                "can_train_models": False,
                "can_generate_signals": False,
                "primary_goal": "measure the ex-post profit ceiling of the cycle under unconstrained hindsight allocation",
            },
            {
                "track_name": "aggressive_no_leak_black_box_track",
                "track_posture": "no_leak_primary_portfolio_experiment",
                "future_information_allowed": False,
                "can_train_models": True,
                "can_generate_signals": False,
                "primary_goal": "maximize total return under point-in-time information with limited regard for drawdown",
            },
            {
                "track_name": "neutral_selective_no_leak_track",
                "track_posture": "no_leak_selective_portfolio_experiment",
                "future_information_allowed": False,
                "can_train_models": True,
                "can_generate_signals": False,
                "primary_goal": "optimize return-drawdown tradeoff, profit factor, and selective participation with cash allowed",
            },
        ]
        model_scope_rows = [
            {
                "model_scope": "level_1_stable_black_box",
                "allowed_models": [
                    "hist_gradient_boosting_classifier",
                    "random_forest_classifier",
                    "xgboost_or_lightgbm_if_available",
                ],
                "priority": 1,
            },
            {
                "model_scope": "level_2_mid_black_box",
                "allowed_models": [
                    "small_mlp_classifier",
                    "gated_mlp_variant",
                    "tabnet_if_available",
                ],
                "priority": 2,
            },
            {
                "model_scope": "level_3_deep_black_box",
                "allowed_models": [
                    "ft_transformer",
                    "sequence_model",
                    "reinforcement_learning_agent",
                ],
                "priority": 3,
            },
        ]
        evaluation_metric_rows = [
            {"metric_name": "total_return", "metric_group": "portfolio"},
            {"metric_name": "max_drawdown", "metric_group": "portfolio"},
            {"metric_name": "profit_factor", "metric_group": "portfolio"},
            {"metric_name": "cash_ratio", "metric_group": "portfolio"},
            {"metric_name": "trade_count", "metric_group": "portfolio"},
            {"metric_name": "phase_capture_rate", "metric_group": "cycle"},
            {"metric_name": "role_selection_quality", "metric_group": "cycle"},
            {"metric_name": "narrative_translation_status", "metric_group": "audit"},
            {"metric_name": "leakage_status", "metric_group": "audit"},
            {"metric_name": "marginal_gain_vs_best", "metric_group": "search_stop"},
        ]

        summary = {
            "acceptance_posture": "freeze_v112bc_cpo_portfolio_objective_protocol_v1",
            "objective_track_count": len(objective_track_rows),
            "no_leak_track_count": 2,
            "oracle_track_count": 1,
            "model_scope_count": len(model_scope_rows),
            "marginal_stop_threshold": 0.005,
            "marginal_stop_patience_rounds": 3,
            "must_output_equity_curve": True,
            "must_output_drawdown_curve": True,
            "must_output_trade_process_trace": True,
            "must_output_portfolio_plot_bundle": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12BC separates hindsight upper-bound benchmarking from no-leak experimental portfolio tracks.",
            "It also freezes a hard stopping rule: if the best new model improves the current best result by less than 0.5% for three rounds, search should stop.",
            "This protocol authorizes black-box exploration, not deployment.",
        ]
        return V112BCCPOPortfolioObjectiveProtocolReport(
            summary=summary,
            objective_track_rows=objective_track_rows,
            model_scope_rows=model_scope_rows,
            evaluation_metric_rows=evaluation_metric_rows,
            interpretation=interpretation,
        )


def write_v112bc_cpo_portfolio_objective_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BCCPOPortfolioObjectiveProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
