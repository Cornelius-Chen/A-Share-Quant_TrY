from pathlib import Path

from a_share_quant.strategy.v112bl_phase_charter_v1 import (
    V112BLPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bl_phase_charter_opens_regime_aware_gate_pilot() -> None:
    analyzer = V112BLPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bd_phase_closure_payload=load_json_report(Path("reports/analysis/v112bd_phase_closure_check_v1.json")),
        v112bh_phase_closure_payload=load_json_report(Path("reports/analysis/v112bh_phase_closure_check_v1.json")),
        v112bi_phase_closure_payload=load_json_report(Path("reports/analysis/v112bi_phase_closure_check_v1.json")),
        v112bj_phase_closure_payload=load_json_report(Path("reports/analysis/v112bj_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bl_now"] is True
    assert result.charter["phase_name"] == "V1.12BL CPO Regime-Aware Gate Pilot"
