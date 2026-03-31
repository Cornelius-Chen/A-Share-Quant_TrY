from pathlib import Path

from a_share_quant.strategy.v112bt_phase_closure_check_v1 import (
    V112BTPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bt_phase_closure_runs() -> None:
    analyzer = V112BTPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bt_phase_check_v1.json")),
    )
    assert result.summary["v112bt_success_criteria_met"] is True
