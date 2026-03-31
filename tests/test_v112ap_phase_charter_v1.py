from pathlib import Path

from a_share_quant.strategy.v112ap_phase_charter_v1 import (
    V112APPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ap_phase_charter_opens_after_v112ao() -> None:
    analyzer = V112APPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ao_phase_closure_payload=load_json_report(Path("reports/analysis/v112ao_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ap_now"] is True
    assert "widen" in result.charter["mission"].lower()
