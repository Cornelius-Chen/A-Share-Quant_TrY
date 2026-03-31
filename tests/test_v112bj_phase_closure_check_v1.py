from pathlib import Path

from a_share_quant.strategy.v112bj_phase_closure_check_v1 import (
    V112BJPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bj_phase_closure_marks_success() -> None:
    analyzer = V112BJPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bj_phase_check_v1.json")),
    )
    assert result.summary["v112bj_success_criteria_met"] is True
