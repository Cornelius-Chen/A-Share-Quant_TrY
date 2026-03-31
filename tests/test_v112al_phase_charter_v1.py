from pathlib import Path

from a_share_quant.strategy.v112al_phase_charter_v1 import (
    V112ALPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112al_phase_charter_opens_after_v112ak_closure() -> None:
    analyzer = V112ALPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ak_phase_closure_payload=load_json_report(Path("reports/analysis/v112ak_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112al_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v112al_cpo_bounded_training_readiness_review_v1"
