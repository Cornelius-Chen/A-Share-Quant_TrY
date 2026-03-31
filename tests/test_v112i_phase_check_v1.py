from pathlib import Path

from a_share_quant.strategy.v112i_phase_check_v1 import (
    V112IPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112i_phase_check_v1_marks_protocol_ready() -> None:
    result = V112IPhaseCheckAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112i_phase_charter_v1.json")),
        protocol_payload=load_json_report(Path("reports/analysis/v112i_label_refinement_review_protocol_v1.json")),
    )
    assert result.summary["acceptance_posture"] == "keep_v112i_as_review_protocol_success"
    assert result.summary["protocol_ready_for_candidate_structure_review"] is True
    assert result.summary["ready_for_phase_closure_next"] is True

