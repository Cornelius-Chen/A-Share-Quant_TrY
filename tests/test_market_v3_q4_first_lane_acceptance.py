from __future__ import annotations

from a_share_quant.strategy.market_v3_q4_first_lane_acceptance import (
    MarketV3Q4FirstLaneAcceptanceAnalyzer,
)


def test_market_v3_q4_first_lane_acceptance_closes_as_opening_led() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "002049", "pnl_delta": 871.89},
            {"symbol": "600584", "pnl_delta": 100.0},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-11-05",
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

    result = MarketV3Q4FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v3_q4_first_lane_as_opening_led_not_carry_breakthrough"
    )
    assert result.summary["top_driver"] == "002049"
    assert result.summary["opening_present"] is True
    assert result.summary["persistence_present"] is False
    assert result.summary["do_open_second_v3_lane_now"] is False
