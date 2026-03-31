from pathlib import Path

from a_share_quant.strategy.v112as_phase_charter_v1 import (
    V112ASPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112as_phase_charter_opens_after_v112ar() -> None:
    analyzer = V112ASPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ar_phase_closure_payload=load_json_report(Path("reports/analysis/v112ar_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112as_now"] is True
    assert "Apply the frozen board/calendar implementation rules" in result.charter["mission"]
