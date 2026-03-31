from pathlib import Path

from a_share_quant.strategy.v112ay_phase_check_v1 import (
    V112AYPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ay_phase_check_keeps_formal_training_closed() -> None:
    analyzer = V112AYPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ay_phase_charter_v1.json")),
        training_layer_review_payload=load_json_report(Path("reports/analysis/v112ay_cpo_guarded_branch_training_layer_review_v1.json")),
    )
    assert result.summary["formal_training_now"] is False
