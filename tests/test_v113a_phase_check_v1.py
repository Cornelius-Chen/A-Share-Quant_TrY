from pathlib import Path

from a_share_quant.strategy.v113a_phase_check_v1 import V113APhaseCheckAnalyzer, load_json_report


def test_v113a_phase_check_v1_keeps_candidate_driver_path_open() -> None:
    result = V113APhaseCheckAnalyzer().analyze(
        state_schema_payload=load_json_report(Path("reports/analysis/v113a_theme_diffusion_state_schema_v1.json"))
    )
    assert result.summary["phase_state_count"] == 4
    assert result.summary["recommended_next_posture"] == "candidate_driver_discovery_or_bounded_state_usage_review"
