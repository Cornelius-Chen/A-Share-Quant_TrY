from __future__ import annotations

from a_share_quant.strategy.market_v2_refresh_q1_drawdown_slice_acceptance import (
    MarketV2RefreshQ1DrawdownSliceAcceptanceAnalyzer,
)


def test_market_v2_refresh_q1_drawdown_slice_acceptance_closes_mixed_slice() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "002415", "pnl_delta": 252.116809},
            {"symbol": "603019", "pnl_delta": 151.888423},
            {"symbol": "002130", "pnl_delta": 20.419022},
        ]
    }
    top_mechanism_payload = {
        "summary": {"cycle_count": 3},
        "mechanism_rows": [
            {"mechanism_type": "entry_suppression_avoidance", "cycle_sign": "negative"},
        ],
    }
    second_mechanism_payload = {
        "summary": {"cycle_count": 1},
        "mechanism_rows": [
            {"mechanism_type": "other_worse_loss_shift", "cycle_sign": "positive"},
        ],
    }

    result = MarketV2RefreshQ1DrawdownSliceAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        top_mechanism_payload=top_mechanism_payload,
        second_mechanism_payload=second_mechanism_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v2_refresh_q1_drawdown_slice_as_avoidance_plus_positive_fragmentation"
    )
    assert result.summary["top_driver_matches_read"] is True
    assert result.summary["do_continue_q1_drawdown_replay"] is False
