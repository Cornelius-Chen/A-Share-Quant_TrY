from pathlib import Path

from a_share_quant.strategy.v112al_phase_closure_check_v1 import (
    V112ALPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112al_phase_closure_keeps_only_bounded_next_posture() -> None:
    analyzer = V112ALPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112al_phase_check_v1.json"))
    )
    assert result.summary["v112al_success_criteria_met"] is True
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "open_extremely_small_core_skeleton_training_pilot_only"
