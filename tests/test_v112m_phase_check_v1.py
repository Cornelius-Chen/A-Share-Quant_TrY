from pathlib import Path

from a_share_quant.strategy.v112m_phase_check_v1 import V112MPhaseCheckAnalyzer, load_json_report


def test_v112m_phase_check_v1_keeps_review_only_posture() -> None:
    result = V112MPhaseCheckAnalyzer().analyze(
        inner_draft_payload=load_json_report(Path("reports/analysis/v112m_mixed_stall_inner_draft_v1.json"))
    )
    assert result.summary["preservable_review_only_inner_candidate_count"] == 2
    assert result.summary["formal_label_split_now"] is False
