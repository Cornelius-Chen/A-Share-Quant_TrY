from pathlib import Path

from a_share_quant.strategy.v112bb_phase_closure_check_v1 import (
    V112BBPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bb_phase_closes_successfully() -> None:
    analyzer = V112BBPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bb_phase_check_v1.json")),
    )
    assert result.summary["v112bb_success_criteria_met"] is True
