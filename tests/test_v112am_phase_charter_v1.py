from pathlib import Path

from a_share_quant.strategy.v112am_phase_charter_v1 import (
    V112AMPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112am_phase_charter_opens_after_v112al_review() -> None:
    analyzer = V112AMPhaseCharterAnalyzer()
    result = analyzer.analyze(
        readiness_review_payload=load_json_report(
            Path("reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json")
        )
    )
    assert result.summary["do_open_v112am_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v112am_cpo_extremely_small_core_skeleton_training_pilot_v1"
