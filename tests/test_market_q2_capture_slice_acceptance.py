from __future__ import annotations

from a_share_quant.strategy.market_q2_capture_slice_acceptance import (
    MarketQ2CaptureSliceAcceptanceAnalyzer,
)


def test_market_q2_capture_slice_acceptance_closes_mixed_slice() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "300502", "pnl_delta": 467.532},
            {"symbol": "002371", "pnl_delta": 185.3549},
            {"symbol": "603259", "pnl_delta": 119.88},
        ]
    }
    persistence_payload = {
        "summary": {
            "specialist_preserved_window": True,
            "persistence_trade_date": "2024-06-17",
        },
        "anchor_divergence": [
            {"exit_reason": "assignment_became_junk"},
            {"exit_reason": "assignment_became_junk"},
        ],
        "persistence_edge": {"specialist_symbol": "300502"},
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-06-05",
        },
        "anchor_blockers": [
            {"assignment_layer": "junk"},
            {"assignment_layer": "junk"},
        ],
        "opening_edge": {"specialist_symbol": "002371"},
    }

    result = MarketQ2CaptureSliceAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        persistence_payload=persistence_payload,
        opening_payload=opening_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_q2_capture_slice_as_mixed_opening_plus_persistence"
    )
    assert result.summary["mixed_mechanism_confirmed"] is True
    assert result.summary["top_pair_covers_slice"] is True
    assert result.summary["do_continue_q2_capture_replay"] is False
