from pathlib import Path

from a_share_quant.strategy.v112bc_phase_check_v1 import (
    V112BCPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bc_phase_check_keeps_protocol_boundary() -> None:
    analyzer = V112BCPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bc_phase_charter_v1.json")),
        protocol_payload=load_json_report(Path("reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json")),
    )
    assert result.summary["objective_track_count"] == 3
    assert result.summary["formal_signal_generation_now"] is False
