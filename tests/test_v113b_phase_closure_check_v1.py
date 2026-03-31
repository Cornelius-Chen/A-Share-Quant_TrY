from pathlib import Path

from a_share_quant.strategy.v113b_phase_closure_check_v1 import (
    V113BPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v113b_phase_closure_check_v1_blocks_auto_driver_promotion() -> None:
    result = V113BPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113b_phase_check_v1.json"))
    )
    assert result.summary["allow_auto_driver_promotion_now"] is False
    assert result.summary["enter_v113b_waiting_state_now"] is True
