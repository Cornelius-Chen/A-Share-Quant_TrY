from pathlib import Path

from a_share_quant.strategy.v112aq_phase_charter_v1 import (
    V112AQPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112aq_phase_charter_opens_after_v112ap() -> None:
    analyzer = V112AQPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ap_phase_closure_payload=load_json_report(Path("reports/analysis/v112ap_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112aq_now"] is True
    assert "implementation patching" in result.charter["mission"]
