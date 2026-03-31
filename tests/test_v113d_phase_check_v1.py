from pathlib import Path

from a_share_quant.strategy.v113d_phase_check_v1 import V113DPhaseCheckAnalyzer, load_json_report


def test_v113d_phase_check_v1_points_to_pause_before_model_line() -> None:
    result = V113DPhaseCheckAnalyzer().analyze(
        archetype_usage_payload=load_json_report(Path("reports/analysis/v113d_bounded_archetype_usage_pass_v1.json"))
    )
    assert result.summary["clean_template_review_asset_count"] == 1
    assert result.summary["recommended_next_posture"] == "preserve_theme_diffusion_archetypes_as_review_assets_and_pause_before_any_model_line"
