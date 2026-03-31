from pathlib import Path

from a_share_quant.strategy.v112bc_phase_closure_check_v1 import (
    V112BCPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bc_phase_closes_successfully() -> None:
    analyzer = V112BCPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bc_phase_check_v1.json")),
    )
    assert result.summary["v112bc_success_criteria_met"] is True
