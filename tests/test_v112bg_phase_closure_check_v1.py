from pathlib import Path

from a_share_quant.strategy.v112bg_phase_closure_check_v1 import (
    V112BGPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bg_phase_closure_closes_successfully() -> None:
    analyzer = V112BGPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bg_phase_check_v1.json")),
    )
    assert result.summary["v112bg_success_criteria_met"] is True
