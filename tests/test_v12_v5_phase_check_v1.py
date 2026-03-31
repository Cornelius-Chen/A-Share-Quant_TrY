from __future__ import annotations

from a_share_quant.strategy.v12_v5_phase_check_v1 import V12V5PhaseCheckAnalyzer


def test_v12_v5_phase_check_opens_second_lane_on_clean_persistence_track() -> None:
    manifest_payload = {
        "summary": {
            "ready_to_bootstrap_market_research_v5_carry_row_diversity_refresh": True,
        },
        "manifest_rows": [
            {"symbol": "000099", "target_training_gap": "true_carry_row"},
            {"symbol": "002273", "target_training_gap": "true_carry_row"},
            {"symbol": "600760", "target_training_gap": "clean_persistence_row"},
            {"symbol": "601989", "target_training_gap": "clean_persistence_row"},
        ],
    }
    training_manifest_payload = {
        "summary": {
            "opening_count_frozen": True,
            "additional_carry_rows_needed": 2,
            "additional_persistence_rows_needed": 2,
        },
        "manifest_rows": [],
    }
    first_lane_payload = {
        "summary": {
            "top_driver": "002273",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_carry_reading": False,
        }
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "002273", "pnl_delta": 36.0},
            {"symbol": "600760", "pnl_delta": -18.4},
            {"symbol": "601989", "pnl_delta": 0.0},
        ]
    }

    result = V12V5PhaseCheckAnalyzer().analyze(
        manifest_payload=manifest_payload,
        training_manifest_payload=training_manifest_payload,
        first_lane_payload=first_lane_payload,
        divergence_payload=divergence_payload,
    )

    assert result.summary["acceptance_posture"] == "open_second_v5_lane_on_clean_persistence_track"
    assert result.summary["recommended_next_track"] == "clean_persistence_row"
    assert result.summary["recommended_next_symbol"] == "600760"
    assert result.summary["do_open_second_v5_lane_now"] is True
