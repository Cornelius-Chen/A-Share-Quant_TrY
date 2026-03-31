from pathlib import Path

from a_share_quant.strategy.v112av_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112av_phase_closure_check_v1 import (
    V112AVPhaseClosureCheckAnalyzer,
)


def test_v112av_phase_closure_check_closes_successfully() -> None:
    analyzer = V112AVPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112av_phase_check_v1.json")),
    )
    assert result.summary["v112av_success_criteria_met"] is True
