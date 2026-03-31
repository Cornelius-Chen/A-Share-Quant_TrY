from pathlib import Path

from a_share_quant.strategy.v112au_phase_charter_v1 import (
    V112AUPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112au_phase_charter_opens_after_v112at() -> None:
    analyzer = V112AUPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112at_phase_closure_payload=load_json_report(Path("reports/analysis/v112at_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112au_now"] is True
    assert "adding branch review rows" in result.charter["mission"]
