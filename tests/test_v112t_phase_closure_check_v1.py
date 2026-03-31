from pathlib import Path

from a_share_quant.strategy.v112t_phase_closure_check_v1 import (
    V112TPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112t_phase_closure_enters_waiting_state() -> None:
    analyzer = V112TPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112t_phase_check_v1.json"))
    )
    assert result.summary["v112t_success_criteria_met"] is True
    assert result.summary["enter_v112t_waiting_state_now"] is True
