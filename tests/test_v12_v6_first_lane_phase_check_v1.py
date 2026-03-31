from __future__ import annotations

from a_share_quant.strategy.v12_v6_first_lane_phase_check_v1 import (
    V12V6FirstLanePhaseCheckAnalyzer,
)


def test_v12_v6_first_lane_phase_check_holds_second_lane() -> None:
    first_lane_acceptance_payload = {
        "summary": {
            "acceptance_posture": "close_market_v6_q3_first_lane_as_opening_led_not_true_carry",
            "top_driver": "600118",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_training_reading": False,
        }
    }
    divergence_payload = {
        "strategy_symbol_summary": [
            {"symbol": "600118", "pnl_delta": 73.369599},
            {"symbol": "002085", "pnl_delta": -122.930616},
            {"symbol": "000738", "pnl_delta": 0.0},
            {"symbol": "300474", "pnl_delta": 0.0},
        ]
    }
    manifest_payload = {
        "manifest_rows": [
            {"symbol": "002085", "target_training_gap": "true_carry_row"},
            {"symbol": "600118", "target_training_gap": "true_carry_row"},
            {"symbol": "000738", "target_training_gap": "clean_persistence_row"},
            {"symbol": "300474", "target_training_gap": "clean_persistence_row"},
        ]
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }

    result = V12V6FirstLanePhaseCheckAnalyzer().analyze(
        first_lane_acceptance_payload=first_lane_acceptance_payload,
        divergence_payload=divergence_payload,
        manifest_payload=manifest_payload,
        training_manifest_payload=training_manifest_payload,
    )

    assert result.summary["acceptance_posture"] == "hold_second_v6_lane_until_new_positive_or_acceptance_grade_candidate"
    assert result.summary["first_lane_opening_led"] is True
    assert result.summary["do_open_second_v6_lane_now"] is False
    assert result.summary["do_run_v6_reassessment_now"] is True
