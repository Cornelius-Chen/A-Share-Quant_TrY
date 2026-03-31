from pathlib import Path

from a_share_quant.strategy.v113d_phase_closure_check_v1 import (
    V113DPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v113d_phase_closure_check_v1_blocks_auto_template_promotion() -> None:
    result = V113DPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v113d_phase_check_v1.json"))
    )
    assert result.summary["allow_auto_model_open_now"] is False
    assert result.summary["allow_auto_execution_schema_now"] is False
    assert result.summary["allow_auto_template_promotion_now"] is False
