from pathlib import Path

from a_share_quant.strategy.v112n_phase_check_v1 import V112NPhaseCheckAnalyzer, load_json_report


def test_v112n_phase_check_v1_detects_no_incremental_gain() -> None:
    result = V112NPhaseCheckAnalyzer().analyze(
        shadow_rerun_payload=load_json_report(Path("reports/analysis/v112n_shadow_rerun_v1.json"))
    )
    assert result.summary["net_incremental_gain_present"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
