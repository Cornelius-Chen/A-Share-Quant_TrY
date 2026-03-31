from pathlib import Path

from a_share_quant.strategy.v112bo_phase_charter_v1 import (
    V112BOPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bo_phase_charter_opens_after_bl_and_bj() -> None:
    analyzer = V112BOPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bl_phase_closure_payload=load_json_report(Path("reports/analysis/v112bl_phase_closure_check_v1.json")),
        v112bj_phase_closure_payload=load_json_report(Path("reports/analysis/v112bj_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bo_now"] is True
