from __future__ import annotations

from a_share_quant.strategy.v12_waiting_state_summary_v1 import (
    V12WaitingStateSummaryAnalyzer,
)


def test_v12_waiting_state_summary_enters_waiting_after_repeated_unchanged_reviews() -> None:
    bottleneck_check_payload = {
        "summary": {
            "acceptance_posture": "keep_v12_primary_bottleneck_as_carry_row_diversity_gap",
            "current_primary_bottleneck": "carry_row_diversity_gap",
        }
    }
    v6_first_lane_phase_check_payload = {
        "summary": {
            "acceptance_posture": "hold_second_v6_lane_until_new_positive_or_acceptance_grade_candidate",
            "do_open_second_v6_lane_now": False,
        }
    }
    v6_reassessment_payload = {
        "summary": {
            "acceptance_posture": "keep_v6_as_active_but_hold_local_second_lane_after_opening_first_lane",
            "do_open_second_v6_lane_now": False,
            "do_prepare_next_refresh_now": False,
        }
    }

    result = V12WaitingStateSummaryAnalyzer().analyze(
        bottleneck_check_payload=bottleneck_check_payload,
        v6_first_lane_phase_check_payload=v6_first_lane_phase_check_payload,
        v6_reassessment_payload=v6_reassessment_payload,
    )

    assert result.summary["acceptance_posture"] == "enter_v12_explicit_waiting_state_after_v6_local_hold"
    assert result.summary["repeated_phase_review_no_change"] is True
    assert result.summary["enter_explicit_waiting_state_now"] is True
    assert result.summary["do_open_v7_now"] is False
