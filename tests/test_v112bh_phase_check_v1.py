from pathlib import Path

from a_share_quant.strategy.v112bh_phase_check_v1 import (
    V112BHPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bh_phase_check_marks_ready_for_closure() -> None:
    analyzer = V112BHPhaseCheckAnalyzer()
    result = analyzer.analyze(
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
