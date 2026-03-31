from __future__ import annotations

from a_share_quant.strategy.market_v5_q2_second_lane_acceptance import (
    MarketV5Q2SecondLaneAcceptanceAnalyzer,
)


def test_market_v5_q2_second_lane_acceptance_closes_as_non_persistence_when_only_opening() -> None:
    phase_check_payload = {
        "summary": {
            "acceptance_posture": "open_second_v5_lane_on_clean_persistence_track",
            "recommended_next_track": "clean_persistence_row",
            "do_open_second_v5_lane_now": True,
        }
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "600760", "pnl_delta": -18.4, "incumbent_trade_count": 3, "challenger_trade_count": 4},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-05-08",
        }
    }
    persistence_payload = {
        "summary": {
            "specialist_preserved_window": False,
            "persistence_trade_date": None,
        }
    }

    result = MarketV5Q2SecondLaneAcceptanceAnalyzer().analyze(
        target_symbol="600760",
        next_symbol_if_closed="601989",
        phase_check_payload=phase_check_payload,
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v5_q2_second_lane_as_opening_led_not_clean_persistence"
    )
    assert result.summary["lane_changes_training_reading"] is False
    assert result.summary["recommended_next_symbol"] == "601989"
