from pathlib import Path

from a_share_quant.strategy.v112bs_phase_closure_check_v1 import (
    V112BSPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bs_phase_closure_runs() -> None:
    analyzer = V112BSPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bs_phase_check_v1.json")),
    )
    assert result.summary["v112bs_success_criteria_met"] is True
