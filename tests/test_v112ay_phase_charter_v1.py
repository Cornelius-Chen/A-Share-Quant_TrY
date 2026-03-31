from pathlib import Path

from a_share_quant.strategy.v112ay_phase_charter_v1 import (
    V112AYPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ay_phase_charter_opens_after_v112ax() -> None:
    analyzer = V112AYPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ax_phase_closure_payload=load_json_report(Path("reports/analysis/v112ax_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ay_now"] is True
