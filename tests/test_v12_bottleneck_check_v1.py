from __future__ import annotations

from a_share_quant.strategy.v12_bottleneck_check_v1 import V12BottleneckCheckAnalyzer


def test_v12_bottleneck_check_keeps_carry_row_diversity_gap() -> None:
    phase_readiness_payload = {
        "summary": {
            "row_diversity_still_missing": True,
            "do_open_new_refresh_batch_now": True,
            "recommended_next_posture": "prepare_later_refresh_batch_to_add_factor_row_diversity",
        }
    }
    next_refresh_design_payload = {
        "summary": {
            "design_posture": "prepare_refresh_batch_for_factor_row_diversity",
            "recommended_batch_posture": "expand_for_carry_row_diversity_not_general_size",
            "recommended_next_batch_name": "market_research_v3_factor_diversity_seed",
        }
    }
    first_lane_acceptance_payload = {
        "summary": {
            "top_driver": "002049",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_carry_reading": False,
        }
    }

    result = V12BottleneckCheckAnalyzer().analyze(
        phase_readiness_payload=phase_readiness_payload,
        next_refresh_design_payload=next_refresh_design_payload,
        first_lane_acceptance_payload=first_lane_acceptance_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
    )
    assert result.summary["current_primary_bottleneck"] == "carry_row_diversity_gap"
    assert result.summary["do_open_second_v3_lane_now"] is False
    assert result.summary["do_change_v12_direction_now"] is False
