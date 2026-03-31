from pathlib import Path

from a_share_quant.strategy.v112bf_phase_check_v1 import (
    V112BFPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bf_phase_check_accepts_aggressive_trace() -> None:
    analyzer = V112BFPhaseCheckAnalyzer()
    result = analyzer.analyze(
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
