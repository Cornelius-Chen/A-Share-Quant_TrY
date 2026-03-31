from pathlib import Path

from a_share_quant.strategy.v112bd_phase_closure_check_v1 import (
    V112BDPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bd_phase_closes_successfully() -> None:
    analyzer = V112BDPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bd_phase_check_v1.json")),
    )
    assert result.summary["v112bd_success_criteria_met"] is True
