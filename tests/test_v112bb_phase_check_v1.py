from pathlib import Path

from a_share_quant.strategy.v112bb_phase_check_v1 import (
    V112BBPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bb_phase_check_keeps_default_pilot_boundary() -> None:
    analyzer = V112BBPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bb_phase_charter_v1.json")),
        pilot_payload=load_json_report(Path("reports/analysis/v112bb_cpo_default_10_row_guarded_layer_pilot_v1.json")),
    )
    assert result.summary["default_10_row_pilot_established"] is True
    assert result.summary["formal_training_now"] is False
