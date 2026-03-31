from pathlib import Path

from a_share_quant.strategy.v112bt_phase_charter_v1 import (
    V112BTPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bt_phase_charter_opens() -> None:
    analyzer = V112BTPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bs_phase_closure_payload=load_json_report(Path("reports/analysis/v112bs_phase_closure_check_v1.json")),
        v112bp_phase_closure_payload=load_json_report(Path("reports/analysis/v112bp_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bt_now"] is True
