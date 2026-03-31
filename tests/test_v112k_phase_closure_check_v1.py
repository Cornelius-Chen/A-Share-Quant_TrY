from pathlib import Path

from a_share_quant.strategy.v112k_phase_closure_check_v1 import (
    V112KPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112k_phase_closure_check_v1_disallows_auto_label_split() -> None:
    result = V112KPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112k_phase_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "close_v112k_as_candidate_substate_draft_success"
    assert result.summary["allow_auto_label_split_now"] is False
