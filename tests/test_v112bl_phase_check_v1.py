from pathlib import Path

from a_share_quant.strategy.v112bl_phase_check_v1 import (
    V112BLPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bl_phase_check_keeps_pilot_open_for_closure() -> None:
    analyzer = V112BLPhaseCheckAnalyzer()
    result = analyzer.analyze(
        regime_gate_pilot_payload=load_json_report(Path("reports/analysis/v112bl_cpo_regime_aware_gate_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
    assert result.summary["trade_count"] >= 0
