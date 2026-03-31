from pathlib import Path

from a_share_quant.strategy.v112ad_phase_closure_check_v1 import (
    V112ADPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112ad_phase_closure_enters_waiting_state() -> None:
    analyzer = V112ADPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112ad_phase_check_v1.json")),
    )
    assert result.summary["v112ad_success_criteria_met"] is True
    assert result.summary["enter_v112ad_waiting_state_now"] is True
