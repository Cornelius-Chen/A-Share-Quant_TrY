from pathlib import Path

from a_share_quant.strategy.v112u_phase_charter_v1 import (
    V112UPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112u_phase_charter_opens_after_v112t() -> None:
    analyzer = V112UPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112t_phase_closure_payload=load_json_report(Path("reports/analysis/v112t_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112u_now"] is True
