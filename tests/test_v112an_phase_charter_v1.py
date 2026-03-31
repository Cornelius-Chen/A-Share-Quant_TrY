from pathlib import Path

from a_share_quant.strategy.v112an_phase_charter_v1 import (
    V112ANPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112an_phase_charter_opens_after_v112am_closure() -> None:
    analyzer = V112ANPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112am_phase_closure_payload=load_json_report(Path("reports/analysis/v112am_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112an_now"] is True
