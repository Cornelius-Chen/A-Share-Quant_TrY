from pathlib import Path

from a_share_quant.strategy.v112az_phase_closure_check_v1 import (
    V112AZPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112az_phase_closure_is_successful() -> None:
    analyzer = V112AZPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112az_phase_check_v1.json")),
    )
    assert result.summary["v112az_success_criteria_met"] is True
