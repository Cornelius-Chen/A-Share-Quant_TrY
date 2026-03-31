from pathlib import Path

from a_share_quant.strategy.v113c_phase_check_v1 import V113CPhaseCheckAnalyzer, load_json_report


def test_v113c_phase_check_v1_points_to_archetype_usage_pass() -> None:
    result = V113CPhaseCheckAnalyzer().analyze(
        state_usage_review_payload=load_json_report(Path("reports/analysis/v113c_bounded_state_usage_review_v1.json"))
    )
    assert result.summary["recommended_next_posture"] == "bounded_archetype_usage_pass_using_schema_review_only_drivers"
