from pathlib import Path

from a_share_quant.strategy.v112aq_cpo_feature_implementation_patch_review_v1 import (
    V112AQCPOFeatureImplementationPatchReviewAnalyzer,
)
from a_share_quant.strategy.v112aq_phase_charter_v1 import load_json_report


def test_v112aq_patch_review_requires_patch_before_row_widen() -> None:
    analyzer = V112AQCPOFeatureImplementationPatchReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aq_phase_charter_v1.json")),
        readiness_payload=load_json_report(Path("reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json")),
        widen_pilot_payload=load_json_report(Path("reports/analysis/v112ap_cpo_bounded_secondary_widen_pilot_v1.json")),
        daily_board_payload=load_json_report(Path("reports/analysis/v112v_cpo_daily_board_chronology_operationalization_v1.json")),
        future_calendar_payload=load_json_report(Path("reports/analysis/v112w_cpo_future_catalyst_calendar_operationalization_v1.json")),
    )
    assert result.summary["should_patch_feature_implementation_before_row_widen"] is True
    assert result.summary["minimum_patch_rule_count"] == 6
