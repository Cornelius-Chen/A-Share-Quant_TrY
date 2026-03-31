from pathlib import Path

from a_share_quant.strategy.v112t_phase_charter_v1 import (
    V112TPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112t_phase_charter_opens_after_v112s() -> None:
    analyzer = V112TPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112s_phase_closure_payload=load_json_report(Path("reports/analysis/v112s_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112t_now"] is True
