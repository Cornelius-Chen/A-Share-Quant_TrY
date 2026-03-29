from __future__ import annotations

from a_share_quant.strategy.market_q3_drawdown_slice_acceptance import (
    MarketQ3DrawdownSliceAcceptanceAnalyzer,
)


def test_market_q3_drawdown_slice_acceptance_closes_cross_strategy_slice() -> None:
    divergence_payloads = [
        {
            "summary": {"strategy_name": "mainline_trend_b"},
            "strategy_symbol_summary": [
                {"symbol": "300308", "pnl_delta": 1781.321},
                {"symbol": "300502", "pnl_delta": 529.7},
            ],
        },
        {
            "summary": {"strategy_name": "mainline_trend_c"},
            "strategy_symbol_summary": [
                {"symbol": "300308", "pnl_delta": 1781.321},
                {"symbol": "300502", "pnl_delta": 529.7},
            ],
        },
    ]
    consistency_payload = {
        "summary": {
            "identical_negative_cycle_map": True,
            "shared_negative_mechanism_count": 3,
        },
        "shared_mechanisms": [
            {
                "mechanism_type": "entry_suppression_avoidance",
                "entry_date": "2024-08-02",
                "exit_date": "2024-08-05",
            }
        ],
    }

    result = MarketQ3DrawdownSliceAcceptanceAnalyzer().analyze(
        divergence_payloads=divergence_payloads,
        consistency_payload=consistency_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse"
    )
    assert result.summary["same_top_driver"] is True
    assert result.summary["do_continue_q3_drawdown_replay"] is False
