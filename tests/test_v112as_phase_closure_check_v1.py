from pathlib import Path

from a_share_quant.strategy.v112as_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112as_phase_closure_check_v1 import (
    V112ASPhaseClosureCheckAnalyzer,
)


def test_v112as_phase_closure_check_closes_successfully() -> None:
    analyzer = V112ASPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112as_phase_check_v1.json")),
    )
    assert result.summary["v112as_success_criteria_met"] is True
    assert result.summary["recommended_next_posture"] == "rerun_current_truth_rows_with_patched_board_and_calendar_features_before_any_row_geometry_widen"
