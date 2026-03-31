from pathlib import Path

from a_share_quant.strategy.v112x_phase_charter_v1 import (
    V112XPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112x_phase_charter_opens_after_v112w() -> None:
    analyzer = V112XPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112w_phase_closure_payload=load_json_report(Path("reports/analysis/v112w_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112x_now"] is True
