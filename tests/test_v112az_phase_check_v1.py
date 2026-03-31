from pathlib import Path

from a_share_quant.strategy.v112az_phase_check_v1 import (
    V112AZPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112az_phase_check_keeps_formal_training_closed() -> None:
    analyzer = V112AZPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112az_phase_charter_v1.json")),
        extension_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
    )
    assert result.summary["formal_training_now"] is False
