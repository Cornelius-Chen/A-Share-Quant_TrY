from __future__ import annotations

from a_share_quant.strategy.residual_cost_acceptance_analysis import ResidualCostAcceptanceAnalyzer


def test_residual_cost_acceptance_analyzer_prefers_freeze_when_gap_is_small_and_local() -> None:
    result = ResidualCostAcceptanceAnalyzer().analyze(
        gate_payload={
            "summary": {
                "mean_max_drawdown_improvement": 0.002504,
                "composite_rank_improvement": 16.444445,
                "mean_total_return_delta": 0.004154,
                "mean_capture_delta": 0.00193,
            }
        },
        drawdown_gap_payload={
            "summary": {
                "weakest_slice": {"dataset_name": "theme_research_v4", "slice_name": "2024_q1"},
                "weakest_dataset_strategy": {"dataset_name": "theme_research_v4", "strategy_name": "mainline_trend_a"},
            }
        },
        chain_payload={
            "summary": {
                "complete_chain_ratio": 1.0,
                "incumbent_missed_cycle_total_pnl": 1969.137,
            }
        },
        relief_gate_payload={
            "passed": False,
            "summary": {
                "mean_max_drawdown_improvement": 0.002509,
            },
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_and_accept_residual_cost"
    assert result.summary["is_localized_theme_pocket"] is True
