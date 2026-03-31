from pathlib import Path

from a_share_quant.strategy.v112be_phase_closure_check_v1 import (
    V112BEPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112be_phase_closure_closes_successfully() -> None:
    analyzer = V112BEPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112be_phase_check_v1.json")),
    )
    assert result.summary["v112be_success_criteria_met"] is True
