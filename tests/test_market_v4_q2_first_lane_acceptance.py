from __future__ import annotations

from a_share_quant.strategy.market_v4_q2_first_lane_acceptance import (
    MarketV4Q2FirstLaneAcceptanceAnalyzer,
)


def test_market_v4_q2_first_lane_acceptance_closes_as_opening_led() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "601919", "pnl_delta": 65.0},
            {"symbol": "002600", "pnl_delta": -18.3},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-05-24",
        },
        "opening_edge": {
            "specialist_assignment_layer": "leader",
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

    result = MarketV4Q2FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v4_q2_first_lane_as_opening_led_not_carry_breakthrough"
    )
    assert result.summary["top_driver"] == "601919"
    assert result.summary["opening_present"] is True
    assert result.summary["persistence_present"] is False
    assert result.summary["do_open_second_v4_lane_now"] is False
