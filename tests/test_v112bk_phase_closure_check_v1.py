from pathlib import Path

from a_share_quant.strategy.v112bk_phase_closure_check_v1 import (
    V112BKPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bk_phase_closure_marks_success() -> None:
    analyzer = V112BKPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bk_phase_check_v1.json")),
    )
    assert result.summary["v112bk_success_criteria_met"] is True
