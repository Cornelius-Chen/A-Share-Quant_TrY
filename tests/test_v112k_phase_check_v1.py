from pathlib import Path

from a_share_quant.strategy.v112k_phase_check_v1 import (
    V112KPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112k_phase_check_v1_keeps_review_only_posture() -> None:
    result = V112KPhaseCheckAnalyzer().analyze(
        draft_payload=load_json_report(Path("reports/analysis/v112k_candidate_substate_draft_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "keep_v112k_as_candidate_substate_draft_success"
    assert result.summary["formal_label_split_now"] is False

