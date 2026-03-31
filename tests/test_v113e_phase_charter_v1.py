from pathlib import Path

from a_share_quant.strategy.v113e_phase_charter_v1 import (
    V113EPhaseCharterAnalyzer,
    load_json_report,
)


def test_v113e_phase_charter_v1_opens_bounded_labeling_pilot() -> None:
    result = V113EPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v113d_phase_closure_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "open_v113e_theme_diffusion_bounded_labeling_pilot_v1"
    assert result.summary["ready_for_pilot_protocol_next"] is True
