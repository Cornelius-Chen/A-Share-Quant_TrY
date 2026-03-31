from pathlib import Path

from a_share_quant.strategy.v112ad_phase_check_v1 import (
    V112ADPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ad_phase_check_keeps_dynamic_role_review_governed() -> None:
    analyzer = V112ADPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ad_phase_charter_v1.json")),
        feature_review_payload=load_json_report(Path("reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json")),
    )
    assert result.summary["allow_auto_feature_promotion_now"] is False
    assert result.summary["allow_auto_training_now"] is False
