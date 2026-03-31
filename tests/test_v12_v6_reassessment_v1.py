from __future__ import annotations

from a_share_quant.strategy.v12_v6_reassessment_v1 import (
    V12V6ReassessmentAnalyzer,
)


def test_v12_v6_reassessment_keeps_v6_active_but_holds_local_second_lane() -> None:
    first_lane_phase_check_payload = {
        "summary": {
            "acceptance_posture": "hold_second_v6_lane_until_new_positive_or_acceptance_grade_candidate",
            "do_open_second_v6_lane_now": False,
            "recommended_next_posture": "run_v12_v6_reassessment_before_any_second_lane",
        }
    }
    specialist_analysis_payload = {
        "top_opportunities": [
            {
                "dataset_name": "market_research_v6_catalyst_supported_carry_persistence_refresh",
                "slice_name": "2024_q3",
                "strategy_name": "mainline_trend_c",
            }
        ]
    }
    bottleneck_check_payload = {
        "summary": {
            "acceptance_posture": "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        }
    }

    result = V12V6ReassessmentAnalyzer().analyze(
        first_lane_phase_check_payload=first_lane_phase_check_payload,
        specialist_analysis_payload=specialist_analysis_payload,
        bottleneck_check_payload=bottleneck_check_payload,
    )

    assert result.summary["acceptance_posture"] == "keep_v6_as_active_but_hold_local_second_lane_after_opening_first_lane"
    assert result.summary["v6_still_active_substrate"] is True
    assert result.summary["do_open_second_v6_lane_now"] is False
    assert result.summary["recommended_next_posture"] == "return_to_v12_level_batch_or_substrate_decision"
