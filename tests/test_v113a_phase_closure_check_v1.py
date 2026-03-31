from pathlib import Path

from a_share_quant.strategy.v113a_phase_closure_check_v1 import V113APhaseClosureCheckAnalyzer, load_json_report


def test_v113a_phase_closure_check_v1_blocks_auto_execution_schema() -> None:
    result = V113APhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113a_phase_check_v1.json"))
    )
    assert result.summary["enter_v113a_waiting_state_now"] is True
    assert result.summary["allow_auto_execution_schema_now"] is False
