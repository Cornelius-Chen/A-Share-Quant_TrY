from pathlib import Path

from a_share_quant.strategy.v112i_phase_charter_v1 import (
    V112IPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112i_phase_charter_v1_opens_from_v112g_waiting_state() -> None:
    payload = load_json_report(Path("reports/analysis/v112g_phase_closure_check_v1.json"))
    result = V112IPhaseCharterAnalyzer().analyze(prior_phase_payload=payload)
    assert result.summary["acceptance_posture"] == "open_v112i_label_refinement_review_protocol"
    assert result.summary["ready_for_protocol_next"] is True

