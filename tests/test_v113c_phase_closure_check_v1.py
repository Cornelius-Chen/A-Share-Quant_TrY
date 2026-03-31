from pathlib import Path

from a_share_quant.strategy.v113c_phase_closure_check_v1 import (
    V113CPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v113c_phase_closure_check_v1_blocks_auto_model_and_execution() -> None:
    result = V113CPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113c_phase_check_v1.json"))
    )
    assert result.summary["allow_auto_model_open_now"] is False
    assert result.summary["allow_auto_execution_schema_now"] is False
    assert result.summary["allow_auto_driver_promotion_now"] is False
