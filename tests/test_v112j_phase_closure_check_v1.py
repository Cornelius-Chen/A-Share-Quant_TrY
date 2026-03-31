from pathlib import Path

from a_share_quant.strategy.v112j_phase_closure_check_v1 import (
    V112JPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112j_phase_closure_check_v1_disallows_auto_label_split() -> None:
    result = V112JPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112j_phase_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "close_v112j_as_candidate_structure_review_success"
    assert result.summary["allow_auto_label_split_now"] is False
