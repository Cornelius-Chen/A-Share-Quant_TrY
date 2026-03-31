from __future__ import annotations

from a_share_quant.strategy.market_v5_q2_last_carry_probe_acceptance import (
    MarketV5Q2LastCarryProbeAcceptanceAnalyzer,
)


def test_market_v5_q2_last_carry_probe_acceptance_closes_as_opening_led() -> None:
    reassessment_payload = {
        "summary": {
            "acceptance_posture": "open_last_v5_true_carry_probe_after_persistence_track_exhaustion",
            "do_open_last_true_carry_probe_now": True,
            "recommended_next_symbol": "000099",
        }
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "000099", "pnl_delta": -7.95, "incumbent_trade_count": 7, "challenger_trade_count": 8},
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_opened_window": True,
            "opening_trade_date": "2024-04-11",
        }
    }
    persistence_payload = {
        "summary": {
            "specialist_preserved_window": False,
            "persistence_trade_date": None,
        }
    }

    result = MarketV5Q2LastCarryProbeAcceptanceAnalyzer().analyze(
        target_symbol="000099",
        reassessment_payload=reassessment_payload,
        divergence_payload=divergence_payload,
        opening_payload=opening_payload,
        persistence_payload=persistence_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_market_v5_q2_last_true_carry_probe_as_opening_led_not_true_carry"
    )
    assert result.summary["phase_allowed_last_true_carry_probe"] is True
    assert result.summary["do_continue_v5_now"] is False
