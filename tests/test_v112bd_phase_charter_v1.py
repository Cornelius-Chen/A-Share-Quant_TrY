from pathlib import Path

from a_share_quant.strategy.v112bd_phase_charter_v1 import (
    V112BDPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bd_phase_charter_opens_after_v112bb() -> None:
    analyzer = V112BDPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bb_phase_closure_payload=load_json_report(Path("reports/analysis/v112bb_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bd_now"] is True
