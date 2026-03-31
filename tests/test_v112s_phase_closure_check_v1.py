from pathlib import Path

from a_share_quant.strategy.v112s_phase_closure_check_v1 import (
    V112SPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112s_phase_closure_enters_waiting_state() -> None:
    analyzer = V112SPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112s_phase_check_v1.json"))
    )
    assert result.summary["v112s_success_criteria_met"] is True
    assert result.summary["enter_v112s_waiting_state_now"] is True
