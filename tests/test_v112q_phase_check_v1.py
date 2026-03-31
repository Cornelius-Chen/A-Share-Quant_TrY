from pathlib import Path

from a_share_quant.strategy.v112q_phase_check_v1 import (
    V112QPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112q_phase_check_keeps_schema_only_posture() -> None:
    analyzer = V112QPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112q_phase_charter_v1.json")),
        schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
    )

    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["allow_auto_feature_promotion_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
