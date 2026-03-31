from pathlib import Path

from a_share_quant.strategy.v113_phase_closure_check_v1 import V113PhaseClosureCheckAnalyzer, load_json_report


def test_v113_phase_closure_check_v1_blocks_auto_model_open() -> None:
    result = V113PhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113_phase_check_v1.json"))
    )
    assert result.summary["enter_v113_waiting_state_now"] is True
    assert result.summary["allow_auto_model_open_now"] is False
