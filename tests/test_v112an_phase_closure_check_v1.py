from pathlib import Path

from a_share_quant.strategy.v112an_phase_closure_check_v1 import (
    V112ANPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112an_phase_closure_requires_owner_choice_next() -> None:
    analyzer = V112ANPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112an_phase_check_v1.json"))
    )
    assert result.summary["v112an_success_criteria_met"] is True
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "owner_decide_whether_to_widen_pilot_or_patch_role_layer"
