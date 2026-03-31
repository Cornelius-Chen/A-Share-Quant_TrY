from pathlib import Path

from a_share_quant.strategy.v112bq_phase_closure_check_v1 import (
    V112BQPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bq_phase_closure_marks_success() -> None:
    analyzer = V112BQPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bq_phase_check_v1.json")),
    )
    assert result.summary["v112bq_success_criteria_met"] is True
