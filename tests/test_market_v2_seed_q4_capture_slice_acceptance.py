from __future__ import annotations

from a_share_quant.strategy.market_v2_seed_q4_capture_slice_acceptance import (
    MarketV2SeedQ4CaptureSliceAcceptanceAnalyzer,
)


def test_market_v2_seed_q4_capture_slice_closes_as_mixed_opening_plus_carry() -> None:
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "603986", "pnl_delta": 1384.533},
            {"symbol": "601398", "pnl_delta": 21.587},
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "candidate_name": "baseline_expansion_branch",
                "closed_trades": [
                    {
                        "entry_date": "2024-09-27",
                        "exit_date": "2024-10-09",
                        "pnl": 2050.324,
                    }
                ],
            }
        ]
    }
    opening_payload = {
        "summary": {
            "specialist_candidate": "baseline_expansion_branch",
            "specialist_opened_window": True,
            "opening_trade_date": "2024-12-12",
        },
        "opening_edge": {
            "specialist_symbol": "603986",
        },
    }

    result = MarketV2SeedQ4CaptureSliceAcceptanceAnalyzer().analyze(
        divergence_payload=divergence_payload,
        timeline_payload=timeline_payload,
        opening_payload=opening_payload,
        slice_start="2024-10-01",
    )

    assert result.summary["acceptance_posture"] == "close_market_v2_seed_q4_capture_slice_as_opening_plus_carry"
    assert result.summary["carry_in_positive_trade_present"] is True
    assert result.summary["do_continue_q4_capture_replay"] is False
