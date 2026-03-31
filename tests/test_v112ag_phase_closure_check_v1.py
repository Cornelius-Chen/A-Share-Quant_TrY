from pathlib import Path

from a_share_quant.strategy.v112ag_phase_closure_check_v1 import (
    V112AGPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112ag_phase_closure_enters_waiting_state() -> None:
    analyzer = V112AGPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112ag_phase_check_v1.json")),
    )
    assert result.summary["v112ag_success_criteria_met"] is True
    assert result.summary["enter_v112ag_waiting_state_now"] is True
    assert result.summary["allow_auto_training_now"] is False
