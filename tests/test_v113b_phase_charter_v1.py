from pathlib import Path

from a_share_quant.strategy.v113b_phase_charter_v1 import (
    V113BPhaseCharterAnalyzer,
    load_json_report,
)


def test_v113b_phase_charter_v1_opens_driver_review() -> None:
    result = V113BPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v113a_phase_closure_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "open_v113b_candidate_mainline_driver_review_v1"
    assert result.summary["ready_for_driver_review_next"] is True
