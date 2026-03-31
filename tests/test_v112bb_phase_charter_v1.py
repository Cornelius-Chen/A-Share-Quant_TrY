from pathlib import Path

from a_share_quant.strategy.v112bb_phase_charter_v1 import (
    V112BBPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bb_phase_charter_opens_after_v112ba() -> None:
    analyzer = V112BBPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ba_phase_closure_payload=load_json_report(Path("reports/analysis/v112ba_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bb_now"] is True
