from pathlib import Path

from a_share_quant.strategy.v112z_phase_check_v1 import (
    V112ZPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112z_phase_check_keeps_training_closed() -> None:
    analyzer = V112ZPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112z_phase_charter_v1.json")),
        protocol_payload=load_json_report(Path("reports/analysis/v112z_cycle_reconstruction_protocol_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
