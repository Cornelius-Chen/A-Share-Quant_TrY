from pathlib import Path

from a_share_quant.strategy.v112bi_phase_closure_check_v1 import (
    V112BIPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bi_phase_closure_marks_success() -> None:
    analyzer = V112BIPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bi_phase_check_v1.json")),
    )
    assert result.summary["v112bi_success_criteria_met"] is True
