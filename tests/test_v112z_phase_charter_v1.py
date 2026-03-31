from pathlib import Path

from a_share_quant.strategy.v112z_phase_charter_v1 import (
    V112ZPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112z_phase_charter_opens_after_v112y() -> None:
    analyzer = V112ZPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112y_phase_closure_payload=load_json_report(Path("reports/analysis/v112y_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112z_now"] is True
