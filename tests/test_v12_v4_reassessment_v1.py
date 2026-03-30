from __future__ import annotations

from a_share_quant.strategy.v12_v4_reassessment_v1 import (
    V12V4ReassessmentAnalyzer,
)


def test_v12_v4_reassessment_keeps_v4_active_but_locally_exhausted() -> None:
    v4_hunt_phase_check_payload = {
        "summary": {
            "acceptance_posture": "pause_v4_lower_priority_tracks_and_reassess_after_high_priority_hunt",
            "high_priority_tracks_exhausted": True,
            "all_checked_high_priority_hunts_inactive": True,
        }
    }
    specialist_analysis_payload = {
        "top_opportunities": [
            {
                "dataset_name": "market_research_v4_carry_row_diversity_refresh",
                "slice_name": "2024_q2",
                "strategy_name": "mainline_trend_a",
            }
        ]
    }
    bottleneck_check_payload = {
        "summary": {
            "acceptance_posture": "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"
        }
    }

    result = V12V4ReassessmentAnalyzer().analyze(
        v4_hunt_phase_check_payload=v4_hunt_phase_check_payload,
        specialist_analysis_payload=specialist_analysis_payload,
        bottleneck_check_payload=bottleneck_check_payload,
    )

    assert result.summary["acceptance_posture"] == "keep_v4_as_active_but_locally_exhausted_substrate"
    assert result.summary["v4_still_active_substrate"] is True
    assert result.summary["checked_region_paused"] is True
    assert result.summary["do_open_lower_priority_v4_tracks_now"] is False
    assert result.summary["recommended_next_posture"] == "return_to_v12_level_batch_or_substrate_decision"
