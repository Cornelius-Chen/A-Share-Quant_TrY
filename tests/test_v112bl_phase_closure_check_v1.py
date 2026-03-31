from pathlib import Path

from a_share_quant.strategy.v112bl_phase_closure_check_v1 import (
    V112BLPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bl_phase_closure_check_closes_as_report_only_success() -> None:
    analyzer = V112BLPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bl_phase_check_v1.json")),
    )
    assert result.summary["v112bl_success_criteria_met"] is True
    assert result.summary["formal_training_now"] is False
