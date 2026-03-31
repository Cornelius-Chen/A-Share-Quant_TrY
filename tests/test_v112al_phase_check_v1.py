from pathlib import Path

from a_share_quant.strategy.v112al_phase_check_v1 import (
    V112ALPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112al_phase_check_keeps_training_closed_and_scope_explicit() -> None:
    analyzer = V112ALPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112al_phase_charter_v1.json")),
        readiness_review_payload=load_json_report(
            Path("reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json")
        ),
    )
    assert result.summary["bounded_training_pilot_lawful_now"] is True
    assert result.summary["representative_training_lawful_now"] is False
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["primary_bottleneck_layer"] == "feature_implementation"
