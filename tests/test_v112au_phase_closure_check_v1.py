from pathlib import Path

from a_share_quant.strategy.v112au_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112au_phase_closure_check_v1 import (
    V112AUPhaseClosureCheckAnalyzer,
)


def test_v112au_phase_closure_check_closes_successfully() -> None:
    analyzer = V112AUPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112au_phase_check_v1.json")),
    )
    assert result.summary["v112au_success_criteria_met"] is True
