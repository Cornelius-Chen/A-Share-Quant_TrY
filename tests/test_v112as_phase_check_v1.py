from pathlib import Path

from a_share_quant.strategy.v112as_phase_check_v1 import V112ASPhaseCheckAnalyzer
from a_share_quant.strategy.v112as_phase_charter_v1 import load_json_report


def test_v112as_phase_check_keeps_widen_closed() -> None:
    analyzer = V112ASPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112as_phase_charter_v1.json")),
        backfill_payload=load_json_report(Path("reports/analysis/v112as_cpo_bounded_implementation_backfill_v1.json")),
    )
    assert result.summary["allow_row_geometry_widen_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
