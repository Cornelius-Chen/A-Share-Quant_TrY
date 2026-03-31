from pathlib import Path

from a_share_quant.strategy.v112ba_phase_check_v1 import (
    V112BAPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ba_phase_check_keeps_formal_training_closed() -> None:
    analyzer = V112BAPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ba_phase_charter_v1.json")),
        replacement_review_payload=load_json_report(Path("reports/analysis/v112ba_cpo_10_row_layer_replacement_review_v1.json")),
    )
    assert result.summary["formal_training_now"] is False
