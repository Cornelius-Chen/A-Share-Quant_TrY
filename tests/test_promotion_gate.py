from __future__ import annotations

from a_share_quant.strategy.promotion_gate import PromotionGateEvaluator


def build_payload() -> dict[str, object]:
    return {
        "comparisons": [
            {
                "dataset_name": "baseline",
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.01,
                    "mainline_capture_ratio": 0.30,
                    "max_drawdown": 0.02,
                },
            },
            {
                "dataset_name": "baseline",
                "candidate_name": "balanced_compromise",
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.015,
                    "mainline_capture_ratio": 0.28,
                    "max_drawdown": 0.018,
                },
            },
            {
                "dataset_name": "theme",
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_c",
                "summary": {
                    "total_return": 0.002,
                    "mainline_capture_ratio": 0.32,
                    "max_drawdown": 0.015,
                },
            },
            {
                "dataset_name": "theme",
                "candidate_name": "balanced_compromise",
                "strategy_name": "mainline_trend_c",
                "summary": {
                    "total_return": 0.006,
                    "mainline_capture_ratio": 0.29,
                    "max_drawdown": 0.012,
                },
            },
        ],
        "extras": {
            "candidate_leaderboard": [
                {
                    "candidate_name": "balanced_compromise",
                    "mean_total_return": 0.0105,
                    "mean_mainline_capture_ratio": 0.285,
                    "mean_max_drawdown": 0.015,
                    "composite_rank_score": 30.0,
                },
                {
                    "candidate_name": "shared_default",
                    "mean_total_return": 0.006,
                    "mean_mainline_capture_ratio": 0.31,
                    "mean_max_drawdown": 0.0175,
                    "composite_rank_score": 35.0,
                },
            ]
        },
    }


def test_promotion_gate_passes_for_clear_compromise_improvement() -> None:
    result = PromotionGateEvaluator().evaluate(
        payload=build_payload(),
        incumbent_name="shared_default",
        challenger_name="balanced_compromise",
        gate_config={
            "min_composite_rank_improvement": 3.0,
            "min_mean_total_return_delta": 0.002,
            "min_mean_max_drawdown_improvement": 0.002,
            "max_mean_capture_regression": 0.05,
            "min_total_return_row_wins": 1,
            "min_dataset_mean_total_return_delta": 0.001,
            "min_dataset_mean_max_drawdown_improvement": 0.001,
            "max_dataset_mean_capture_regression": 0.05,
        },
    )

    assert result.passed is True
    assert result.summary["composite_rank_improvement"] == 5.0
    assert result.summary["mean_total_return_delta"] == 0.0045
    assert result.summary["mean_max_drawdown_improvement"] == 0.0025
    assert result.row_win_counts["balanced_compromise"]["total_return"] == 2
    assert result.dataset_deltas[0]["dataset_name"] == "baseline"
    assert result.dataset_deltas[1]["dataset_name"] == "theme"


def test_promotion_gate_fails_when_capture_regression_is_too_large() -> None:
    result = PromotionGateEvaluator().evaluate(
        payload=build_payload(),
        incumbent_name="shared_default",
        challenger_name="balanced_compromise",
        gate_config={
            "min_composite_rank_improvement": 3.0,
            "min_mean_total_return_delta": 0.002,
            "min_mean_max_drawdown_improvement": 0.002,
            "max_mean_capture_regression": 0.01,
            "min_total_return_row_wins": 1,
            "min_dataset_mean_total_return_delta": 0.001,
            "min_dataset_mean_max_drawdown_improvement": 0.001,
            "max_dataset_mean_capture_regression": 0.05,
        },
    )

    assert result.passed is False
    capture_check = next(check for check in result.checks if check["name"] == "mean_capture_regression")
    assert capture_check["passed"] is False


def test_promotion_gate_fails_when_any_dataset_regresses_too_much() -> None:
    result = PromotionGateEvaluator().evaluate(
        payload=build_payload(),
        incumbent_name="shared_default",
        challenger_name="balanced_compromise",
        gate_config={
            "min_composite_rank_improvement": 3.0,
            "min_mean_total_return_delta": 0.002,
            "min_mean_max_drawdown_improvement": 0.002,
            "max_mean_capture_regression": 0.05,
            "min_total_return_row_wins": 1,
            "min_dataset_mean_total_return_delta": 0.001,
            "min_dataset_mean_max_drawdown_improvement": 0.001,
            "max_dataset_mean_capture_regression": 0.015,
        },
    )

    assert result.passed is False
    dataset_capture_check = next(
        check for check in result.checks if check["name"] == "max_dataset_mean_capture_regression"
    )
    assert dataset_capture_check["passed"] is False
