from pathlib import Path

from a_share_quant.strategy.v112w_phase_charter_v1 import (
    V112WPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112w_phase_charter_opens_after_v112v() -> None:
    analyzer = V112WPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112v_phase_closure_payload=load_json_report(Path("reports/analysis/v112v_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112w_now"] is True
