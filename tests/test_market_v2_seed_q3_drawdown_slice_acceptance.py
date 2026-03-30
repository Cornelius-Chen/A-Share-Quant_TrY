from __future__ import annotations

from a_share_quant.strategy.market_v2_seed_q3_drawdown_slice_acceptance import (
    MarketV2SeedQ3DrawdownSliceAcceptanceAnalyzer,
)


def test_market_v2_seed_q3_drawdown_slice_acceptance_closes_mixed_slice() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "603986", "pnl_delta": 333.887},
            {"symbol": "601138", "pnl_delta": 172.885},
            {"symbol": "601398", "pnl_delta": 20.085},
        ]
    }
    mechanism_payload = {
        "summary": {"cycle_count": 2},
        "mechanism_rows": [
            {"mechanism_type": "entry_suppression_avoidance", "cycle_sign": "negative"},
            {"mechanism_type": "entry_suppression_opportunity_cost", "cycle_sign": "positive"},
        ],
    }

    result = MarketV2SeedQ3DrawdownSliceAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        mechanism_payload=mechanism_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost"
    )
    assert result.summary["top_driver_matches_read"] is True
    assert result.summary["do_continue_q3_drawdown_replay"] is False
