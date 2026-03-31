from pathlib import Path

from a_share_quant.strategy.v112y_phase_charter_v1 import (
    V112YPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112y_phase_charter_opens_after_v112x() -> None:
    analyzer = V112YPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112x_phase_closure_payload=load_json_report(Path("reports/analysis/v112x_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112y_now"] is True
