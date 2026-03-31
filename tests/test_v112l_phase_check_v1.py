from pathlib import Path

from a_share_quant.strategy.v112l_phase_check_v1 import V112LPhaseCheckAnalyzer, load_json_report


def test_v112l_phase_check_v1_keeps_review_only_posture() -> None:
    result = V112LPhaseCheckAnalyzer().analyze(
        owner_review_payload=load_json_report(Path("reports/analysis/v112l_candidate_substate_owner_review_v1.json"))
    )
    assert result.summary["preserved_review_only_count"] == 2
    assert result.summary["formal_label_split_now"] is False
