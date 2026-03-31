from pathlib import Path

from a_share_quant.strategy.v112am_phase_closure_check_v1 import (
    V112AMPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112am_phase_closure_preserves_owner_review_next() -> None:
    analyzer = V112AMPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112am_phase_check_v1.json"))
    )
    assert result.summary["v112am_success_criteria_met"] is True
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "owner_review_of_core_skeleton_pilot_results"
