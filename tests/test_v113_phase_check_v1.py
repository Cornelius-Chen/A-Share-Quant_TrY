from pathlib import Path

from a_share_quant.strategy.v113_phase_check_v1 import V113PhaseCheckAnalyzer, load_json_report


def test_v113_phase_check_v1_keeps_schema_first_posture() -> None:
    result = V113PhaseCheckAnalyzer().analyze(
        template_entry_payload=load_json_report(Path("reports/analysis/v113_template_entry_v1.json"))
    )
    assert result.summary["selected_template_family"] == "theme_diffusion_carry"
    assert result.summary["schema_first_posture"] is True
