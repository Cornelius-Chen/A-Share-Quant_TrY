from pathlib import Path

from a_share_quant.strategy.v112bh_phase_closure_check_v1 import (
    V112BHPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bh_phase_closure_closes_successfully() -> None:
    analyzer = V112BHPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bh_phase_check_v1.json")),
    )
    assert result.summary["v112bh_success_criteria_met"] is True
