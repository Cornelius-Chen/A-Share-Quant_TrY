from pathlib import Path

from a_share_quant.strategy.v112l_phase_closure_check_v1 import V112LPhaseClosureCheckAnalyzer, load_json_report


def test_v112l_phase_closure_check_v1_blocks_auto_inner_drafting() -> None:
    result = V112LPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112l_phase_check_v1.json"))
    )
    assert result.summary["enter_v112l_waiting_state_now"] is True
    assert result.summary["allow_auto_inner_drafting_now"] is False
    assert result.summary["allow_formal_label_split_now"] is False
