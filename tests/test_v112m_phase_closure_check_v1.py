from pathlib import Path

from a_share_quant.strategy.v112m_phase_closure_check_v1 import V112MPhaseClosureCheckAnalyzer, load_json_report


def test_v112m_phase_closure_check_v1_blocks_auto_schema_change() -> None:
    result = V112MPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112m_phase_check_v1.json"))
    )
    assert result.summary["enter_v112m_waiting_state_now"] is True
    assert result.summary["allow_auto_schema_change_now"] is False
    assert result.summary["allow_auto_follow_up_now"] is False
