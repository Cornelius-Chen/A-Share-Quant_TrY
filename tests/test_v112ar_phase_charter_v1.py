from pathlib import Path

from a_share_quant.strategy.v112ar_phase_charter_v1 import (
    V112ARPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ar_phase_charter_opens_after_v112aq() -> None:
    analyzer = V112ARPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112aq_phase_closure_payload=load_json_report(Path("reports/analysis/v112aq_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ar_now"] is True
    assert "board series" in result.charter["mission"]
