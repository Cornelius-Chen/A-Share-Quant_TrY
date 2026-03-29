from __future__ import annotations

from a_share_quant.strategy.market_q4_drawdown_slice_acceptance import (
    MarketQ4DrawdownSliceAcceptanceAnalyzer,
)


def test_market_q4_drawdown_slice_acceptance_closes_mixed_slice() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "002371", "pnl_delta": 1509.5429},
            {"symbol": "000977", "pnl_delta": 599.969},
            {"symbol": "000858", "pnl_delta": 521.068},
        ]
    }
    first_mechanism_payload = {
        "summary": {"strategy_name": "mainline_trend_c"},
        "mechanism_rows": [
            {
                "mechanism_type": "entry_suppression_avoidance",
                "cycle_sign": "negative",
            }
        ],
    }
    second_mechanism_payload = {
        "summary": {"strategy_name": "mainline_trend_c"},
        "mechanism_rows": [
            {
                "mechanism_type": "preemptive_loss_avoidance_shift",
                "cycle_sign": "negative",
            },
            {
                "mechanism_type": "earlier_exit_loss_reduction",
                "cycle_sign": "negative",
            },
        ],
    }

    result = MarketQ4DrawdownSliceAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        first_mechanism_payload=first_mechanism_payload,
        second_mechanism_payload=second_mechanism_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix"
    )
    assert result.summary["first_symbol_is_clean_avoidance"] is True
    assert result.summary["second_symbol_expands_beyond_avoidance"] is True
    assert result.summary["do_continue_q4_drawdown_replay"] is False
