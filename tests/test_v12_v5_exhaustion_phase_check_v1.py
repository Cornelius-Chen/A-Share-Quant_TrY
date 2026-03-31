from __future__ import annotations

from a_share_quant.strategy.v12_v5_exhaustion_phase_check_v1 import (
    V12V5ExhaustionPhaseCheckAnalyzer,
)


def test_v12_v5_exhaustion_phase_check_prepares_next_refresh_entry() -> None:
    v5_reassessment_payload = {
        "summary": {
            "do_open_last_true_carry_probe_now": True,
            "clean_persistence_track_exhausted": True,
        }
    }
    last_true_carry_probe_payload = {
        "summary": {
            "acceptance_posture": "close_market_v5_q2_last_true_carry_probe_as_opening_led_not_true_carry",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_training_reading": False,
            "do_continue_current_symbol_now": False,
            "do_continue_v5_now": False,
        }
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }
    catalyst_phase_check_payload = {
        "summary": {
            "keep_branch_report_only": True,
        }
    }

    result = V12V5ExhaustionPhaseCheckAnalyzer().analyze(
        v5_reassessment_payload=v5_reassessment_payload,
        last_true_carry_probe_payload=last_true_carry_probe_payload,
        training_manifest_payload=training_manifest_payload,
        catalyst_phase_check_payload=catalyst_phase_check_payload,
    )

    assert result.summary["acceptance_posture"] == "close_v5_as_bounded_but_non_repairing_refresh"
    assert result.summary["v5_manifest_exhausted"] is True
    assert result.summary["remaining_true_carry_gap"] == 2
    assert result.summary["do_prepare_next_refresh_entry_now"] is True
