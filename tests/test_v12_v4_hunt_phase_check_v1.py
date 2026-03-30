from __future__ import annotations

from a_share_quant.strategy.v12_v4_hunt_phase_check_v1 import (
    V12V4HuntPhaseCheckAnalyzer,
)


def test_v12_v4_hunt_phase_check_pauses_after_inactive_high_priority_tracks() -> None:
    hunting_strategy_payload = {
        "hunt_rows": [
            {"symbol": "000725", "target_row_diversity": "basis_spread_diversity"},
            {"symbol": "600703", "target_row_diversity": "basis_spread_diversity"},
            {"symbol": "600150", "target_row_diversity": "carry_duration_diversity"},
            {"symbol": "601127", "target_row_diversity": "carry_duration_diversity"},
            {"symbol": "002600", "target_row_diversity": "cross_dataset_carry_reuse"},
        ]
    }
    bottleneck_check_payload = {
        "summary": {"acceptance_posture": "keep_v12_primary_bottleneck_as_carry_row_diversity_gap"}
    }
    inactive = {
        "summary": {
            "acceptance_posture": "close_market_v4_q2_symbol_hunt_as_no_active_structural_lane",
            "target_symbol": "dummy",
            "lane_changes_carry_reading": False,
        }
    }
    result = V12V4HuntPhaseCheckAnalyzer().analyze(
        hunting_strategy_payload=hunting_strategy_payload,
        bottleneck_check_payload=bottleneck_check_payload,
        first_hunt_payload={**inactive, "summary": {**inactive["summary"], "target_symbol": "000725"}},
        second_hunt_payload={**inactive, "summary": {**inactive["summary"], "target_symbol": "600703"}},
        third_hunt_payload={**inactive, "summary": {**inactive["summary"], "target_symbol": "600150"}},
        fourth_hunt_payload={**inactive, "summary": {**inactive["summary"], "target_symbol": "601127"}},
    )

    assert (
        result.summary["acceptance_posture"]
        == "pause_v4_lower_priority_tracks_and_reassess_after_high_priority_hunt"
    )
    assert result.summary["high_priority_tracks_exhausted"] is True
    assert result.summary["all_checked_high_priority_hunts_inactive"] is True
    assert result.summary["do_open_lower_priority_tracks_now"] is False
