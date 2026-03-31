from pathlib import Path

from a_share_quant.strategy.v112ab_phase_closure_check_v1 import (
    V112ABPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112ab_phase_closure_enters_waiting_state() -> None:
    analyzer = V112ABPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112ab_phase_check_v1.json"))
    )
    assert result.summary["enter_v112ab_waiting_state_now"] is True
