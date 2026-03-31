from pathlib import Path

from a_share_quant.strategy.v112v_phase_charter_v1 import (
    V112VPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112v_phase_charter_opens_after_v112u() -> None:
    analyzer = V112VPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112u_phase_closure_payload=load_json_report(Path("reports/analysis/v112u_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112v_now"] is True
