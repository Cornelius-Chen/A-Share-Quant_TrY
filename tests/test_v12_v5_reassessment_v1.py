from __future__ import annotations

from a_share_quant.strategy.v12_v5_reassessment_v1 import V12V5ReassessmentAnalyzer


def test_v12_v5_reassessment_opens_last_true_carry_probe() -> None:
    manifest_payload = {
        "manifest_rows": [
            {"symbol": "000099", "target_training_gap": "true_carry_row"},
            {"symbol": "002273", "target_training_gap": "true_carry_row"},
            {"symbol": "600760", "target_training_gap": "clean_persistence_row"},
            {"symbol": "601989", "target_training_gap": "clean_persistence_row"},
        ]
    }
    first_lane_payload = {
        "summary": {
            "top_driver": "002273",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_carry_reading": False,
        }
    }
    phase_check_payload = {
        "summary": {
            "do_open_second_v5_lane_now": True,
        }
    }
    second_lane_payload = {
        "summary": {
            "acceptance_posture": "close_market_v5_q2_second_lane_as_divergent_but_not_acceptance_grade",
        }
    }
    third_lane_payload = {
        "summary": {
            "acceptance_posture": "close_market_v5_q2_second_lane_as_no_active_structural_lane",
        }
    }

    result = V12V5ReassessmentAnalyzer().analyze(
        manifest_payload=manifest_payload,
        first_lane_payload=first_lane_payload,
        phase_check_payload=phase_check_payload,
        second_lane_payload=second_lane_payload,
        third_lane_payload=third_lane_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "open_last_v5_true_carry_probe_after_persistence_track_exhaustion"
    )
    assert result.summary["clean_persistence_track_exhausted"] is True
    assert result.summary["recommended_next_symbol"] == "000099"
    assert result.summary["do_open_last_true_carry_probe_now"] is True
