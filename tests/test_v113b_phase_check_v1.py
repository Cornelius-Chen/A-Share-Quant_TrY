from pathlib import Path

from a_share_quant.strategy.v113b_phase_check_v1 import V113BPhaseCheckAnalyzer, load_json_report


def test_v113b_phase_check_v1_points_to_bounded_state_usage_review() -> None:
    result = V113BPhaseCheckAnalyzer().analyze(
        driver_review_payload=load_json_report(Path("reports/analysis/v113b_candidate_mainline_driver_review_v1.json"))
    )
    assert result.summary["bounded_state_usage_ready_count"] == 4
    assert result.summary["recommended_next_posture"] == "bounded_state_usage_review_on_high_priority_mainline_drivers_only"
