from __future__ import annotations

from a_share_quant.strategy.market_v4_q2_symbol_hunt_acceptance import (
    MarketV4Q2SymbolHuntAcceptanceAnalyzer,
)


def test_market_v4_q2_symbol_hunt_acceptance_closes_inactive_symbol() -> None:
    hunting_strategy_payload = {
        "hunt_rows": [
            {
                "symbol": "000725",
                "target_row_diversity": "basis_spread_diversity",
                "carry_row_hypothesis": "Probe lower-basis hardware carry rows.",
                "hunt_posture": "hunt_next",
            },
            {
                "symbol": "600703",
                "target_row_diversity": "basis_spread_diversity",
                "carry_row_hypothesis": "Probe mid-basis hardware carry rows.",
                "hunt_posture": "hunt_next",
            },
        ]
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {
                "symbol": "000725",
                "incumbent_trade_count": 2,
                "challenger_trade_count": 2,
                "pnl_delta": 0.0,
            }
        ]
    }
    opening_payload = {"summary": {"specialist_opened_window": False, "opening_trade_date": None}}
    persistence_payload = {
        "summary": {"specialist_preserved_window": False, "persistence_trade_date": None}
    }

    result = MarketV4Q2SymbolHuntAcceptanceAnalyzer().analyze(
        target_symbol="000725",
        excluded_symbols=["000725"],
        hunting_strategy_payload=hunting_strategy_payload,
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v4_q2_symbol_hunt_as_no_active_structural_lane"
    )
    assert result.summary["target_symbol"] == "000725"
    assert result.summary["lane_changes_carry_reading"] is False
    assert result.summary["recommended_next_symbol"] == "600703"


def test_market_v4_q2_symbol_hunt_acceptance_skips_previously_closed_symbols() -> None:
    hunting_strategy_payload = {
        "hunt_rows": [
            {"symbol": "000725", "target_row_diversity": "basis_spread_diversity", "hunt_posture": "hunt_next"},
            {"symbol": "600703", "target_row_diversity": "basis_spread_diversity", "hunt_posture": "hunt_next"},
            {"symbol": "600150", "target_row_diversity": "carry_duration_diversity", "hunt_posture": "hunt_next"},
        ]
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "600703", "incumbent_trade_count": 2, "challenger_trade_count": 2, "pnl_delta": 0.0}
        ]
    }
    opening_payload = {"summary": {"specialist_opened_window": False}}
    persistence_payload = {"summary": {"specialist_preserved_window": False}}

    result = MarketV4Q2SymbolHuntAcceptanceAnalyzer().analyze(
        target_symbol="600703",
        excluded_symbols=["000725", "600703"],
        hunting_strategy_payload=hunting_strategy_payload,
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert result.summary["recommended_next_symbol"] == "600150"
