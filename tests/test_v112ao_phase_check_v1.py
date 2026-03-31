from pathlib import Path

from a_share_quant.strategy.v112ao_phase_check_v1 import (
    V112AOPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ao_phase_check_preserves_report_only_boundary() -> None:
    analyzer = V112AOPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ao_phase_charter_v1.json")),
        patch_pilot_payload=load_json_report(Path("reports/analysis/v112ao_cpo_role_layer_patch_pilot_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
