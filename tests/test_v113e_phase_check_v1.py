from pathlib import Path

from a_share_quant.strategy.v113e_phase_check_v1 import V113EPhaseCheckAnalyzer, load_json_report


def test_v113e_phase_check_v1_points_to_bounded_pilot_data_assembly() -> None:
    result = V113EPhaseCheckAnalyzer().analyze(
        pilot_protocol_payload=load_json_report(Path("reports/analysis/v113e_pilot_protocol_v1.json"))
    )
    assert result.summary["recommended_next_posture"] == "bounded_pilot_data_assembly_for_selected_theme_diffusion_archetype"
