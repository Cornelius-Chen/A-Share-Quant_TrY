from pathlib import Path

from a_share_quant.strategy.v112i_phase_closure_check_v1 import (
    V112IPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112i_phase_closure_check_v1_enters_waiting_state() -> None:
    result = V112IPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112i_phase_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "close_v112i_as_review_protocol_success"
    assert result.summary["enter_v112i_waiting_state_now"] is True
    assert result.summary["allow_auto_label_split_now"] is False
