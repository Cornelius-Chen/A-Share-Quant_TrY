from __future__ import annotations

from a_share_quant.strategy.market_v6_q3_first_lane_acceptance import (
    MarketV6Q3FirstLaneAcceptanceAnalyzer,
)


def test_market_v6_q3_first_lane_acceptance_prefers_clean_persistence_reading() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "600118", "pnl_delta": 73.36},
            {"symbol": "002085", "pnl_delta": -122.93},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-07-26",
        },
        "opening_edge": {
            "specialist_assignment_layer": "late_mover",
        },
    }
    persistence_payload = {
        "summary": {
            "specialist_preserved_window": True,
            "persistence_trade_date": "2024-09-20",
        }
    }

    result = MarketV6Q3FirstLaneAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert result.summary["acceptance_posture"] == "close_market_v6_q3_first_lane_as_clean_persistence_not_true_carry"
    assert result.summary["top_driver"] == "600118"
    assert result.summary["lane_changes_training_reading"] is True
