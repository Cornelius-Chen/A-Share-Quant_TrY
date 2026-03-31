from pathlib import Path

from a_share_quant.strategy.v112bf_phase_charter_v1 import (
    V112BFPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bf_phase_charter_opens_aggressive_track() -> None:
    analyzer = V112BFPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112be_phase_closure_payload=load_json_report(Path("reports/analysis/v112be_phase_closure_check_v1.json")),
        v112bb_phase_closure_payload=load_json_report(Path("reports/analysis/v112bb_phase_closure_check_v1.json")),
        v112bc_phase_closure_payload=load_json_report(Path("reports/analysis/v112bc_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bf_now"] is True
