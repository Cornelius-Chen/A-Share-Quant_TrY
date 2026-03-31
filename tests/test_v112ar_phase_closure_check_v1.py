from pathlib import Path

from a_share_quant.strategy.v112ar_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112ar_phase_closure_check_v1 import (
    V112ARPhaseClosureCheckAnalyzer,
)


def test_v112ar_phase_closure_check_closes_successfully() -> None:
    analyzer = V112ARPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112ar_phase_check_v1.json")),
    )
    assert result.summary["v112ar_success_criteria_met"] is True
    assert result.summary["recommended_next_posture"] == "bounded_implementation_backfill_on_current_truth_rows"
