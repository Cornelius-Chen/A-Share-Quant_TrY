from pathlib import Path

from a_share_quant.strategy.v113c_phase_charter_v1 import (
    V113CPhaseCharterAnalyzer,
    load_json_report,
)


def test_v113c_phase_charter_v1_opens_bounded_state_usage_review() -> None:
    result = V113CPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v113b_phase_closure_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "open_v113c_bounded_state_usage_review_v1"
    assert result.summary["ready_for_state_usage_review_next"] is True
