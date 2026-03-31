from pathlib import Path

from a_share_quant.strategy.v112ax_phase_charter_v1 import (
    V112AXPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ax_phase_charter_opens_after_v112aw() -> None:
    analyzer = V112AXPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112aw_phase_closure_payload=load_json_report(Path("reports/analysis/v112aw_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ax_now"] is True
