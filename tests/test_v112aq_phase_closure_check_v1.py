from pathlib import Path

from a_share_quant.strategy.v112aq_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112aq_phase_closure_check_v1 import (
    V112AQPhaseClosureCheckAnalyzer,
)


def test_v112aq_phase_closure_check_closes_successfully() -> None:
    analyzer = V112AQPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112aq_phase_check_v1.json")),
    )
    assert result.summary["v112aq_success_criteria_met"] is True
    assert result.summary["allow_row_geometry_widen_now"] is False
