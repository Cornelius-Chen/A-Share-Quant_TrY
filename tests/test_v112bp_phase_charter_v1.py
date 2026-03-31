from pathlib import Path

from a_share_quant.strategy.v112bp_phase_charter_v1 import (
    V112BPPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bp_phase_charter_opens_after_prereqs() -> None:
    analyzer = V112BPPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bk_phase_closure_payload=load_json_report(Path("reports/analysis/v112bk_phase_closure_check_v1.json")),
        v112bd_phase_closure_payload=load_json_report(Path("reports/analysis/v112bd_phase_closure_check_v1.json")),
        v112bh_phase_closure_payload=load_json_report(Path("reports/analysis/v112bh_phase_closure_check_v1.json")),
        v112bo_phase_closure_payload=load_json_report(Path("reports/analysis/v112bo_phase_closure_check_v1.json")),
        v112bb_phase_closure_payload=load_json_report(Path("reports/analysis/v112bb_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bp_now"] is True
