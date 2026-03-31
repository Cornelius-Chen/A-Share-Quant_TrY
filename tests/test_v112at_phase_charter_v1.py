from pathlib import Path

from a_share_quant.strategy.v112at_phase_charter_v1 import (
    V112ATPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112at_phase_charter_opens_after_v112as() -> None:
    analyzer = V112ATPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112as_phase_closure_payload=load_json_report(Path("reports/analysis/v112as_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112at_now"] is True
    assert "Rerun the current truth-row pilot" in result.charter["mission"]
