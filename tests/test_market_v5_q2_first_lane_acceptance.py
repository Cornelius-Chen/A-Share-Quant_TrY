from __future__ import annotations

from a_share_quant.strategy.market_v5_q2_first_lane_acceptance import (
    MarketV5Q2FirstLaneAcceptanceAnalyzer,
)


def test_market_v5_q2_first_lane_acceptance_closes_as_opening_led() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "002273", "pnl_delta": 36.0},
            {"symbol": "600760", "pnl_delta": -18.4},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-05-13",
        },
        "opening_edge": {
            "specialist_assignment_layer": "late_mover",
        },
        "anchor_blockers": [
            {
                "permission_allowed": True,
                "assignment_layer": "junk",
                "emitted_actions": [],
            },
            {
                "permission_allowed": True,
                "assignment_layer": "junk",
                "emitted_actions": [],
            },
        ],
    }
    persistence_payload = {
        "summary": {
            "specialist_preserved_window": False,
            "persistence_trade_date": None,
        }
    }

    result = MarketV5Q2FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v5_q2_first_lane_as_opening_led_not_carry_breakthrough"
    )
    assert result.summary["top_driver"] == "002273"
    assert result.summary["opening_present"] is True
    assert result.summary["persistence_present"] is False
    assert result.summary["do_open_second_v5_lane_now"] is False
