from pathlib import Path

from a_share_quant.strategy.v112ak_phase_check_v1 import (
    V112AKPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ak_phase_check_keeps_training_closed() -> None:
    analyzer = V112AKPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ak_phase_charter_v1.json")),
        feature_binding_payload=load_json_report(Path("reports/analysis/v112ak_cpo_bounded_feature_binding_review_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "bounded_training_readiness_review_with_binding_gaps_explicit"
