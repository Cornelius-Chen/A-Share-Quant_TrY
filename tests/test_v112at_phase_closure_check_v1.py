from pathlib import Path

from a_share_quant.strategy.v112at_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112at_phase_closure_check_v1 import (
    V112ATPhaseClosureCheckAnalyzer,
)


def test_v112at_phase_closure_check_closes_successfully() -> None:
    analyzer = V112ATPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112at_phase_check_v1.json")),
    )
    assert result.summary["v112at_success_criteria_met"] is True
    assert result.summary["allow_row_geometry_widen_now"] is True
