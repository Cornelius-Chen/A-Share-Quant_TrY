from pathlib import Path

from a_share_quant.strategy.v112r_phase_charter_v1 import (
    V112RPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112r_phase_charter_opens_after_v112q() -> None:
    analyzer = V112RPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112q_phase_closure_payload=load_json_report(Path("reports/analysis/v112q_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112r_now"] is True
