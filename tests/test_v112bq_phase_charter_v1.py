from pathlib import Path

from a_share_quant.strategy.v112bq_phase_charter_v1 import (
    V112BQPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bq_phase_charter_opens_from_completed_prerequisites() -> None:
    analyzer = V112BQPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bp_phase_closure_payload=load_json_report(Path("reports/analysis/v112bp_phase_closure_check_v1.json")),
        v112bh_phase_closure_payload=load_json_report(Path("reports/analysis/v112bh_phase_closure_check_v1.json")),
        v112bn_phase_closure_payload=load_json_report(Path("reports/analysis/v112bn_phase_closure_check_v1.json")),
        v112bo_phase_closure_payload=load_json_report(Path("reports/analysis/v112bo_phase_closure_check_v1.json")),
        v112bl_phase_closure_payload=load_json_report(Path("reports/analysis/v112bl_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bq_now"] is True

