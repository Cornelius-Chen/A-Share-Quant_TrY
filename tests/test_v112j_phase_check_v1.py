from pathlib import Path

from a_share_quant.strategy.v112j_phase_check_v1 import (
    V112JPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112j_phase_check_v1_keeps_follow_up_bounded() -> None:
    result = V112JPhaseCheckAnalyzer().analyze(
        candidate_review_payload=load_json_report(Path("reports/analysis/v112j_candidate_structure_review_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "keep_v112j_as_candidate_structure_review_success"
    assert result.summary["bounded_follow_up_stage"] == "high_level_consolidation"

