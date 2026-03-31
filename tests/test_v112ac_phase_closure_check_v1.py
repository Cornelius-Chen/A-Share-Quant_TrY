from pathlib import Path

from a_share_quant.strategy.v112ac_phase_closure_check_v1 import (
    V112ACPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112ac_phase_closure_enters_waiting_state() -> None:
    analyzer = V112ACPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112ac_phase_check_v1.json")),
    )
    assert result.summary["v112ac_success_criteria_met"] is True
    assert result.summary["enter_v112ac_waiting_state_now"] is True
