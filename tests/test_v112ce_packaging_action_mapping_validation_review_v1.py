from pathlib import Path

from a_share_quant.strategy.v112ce_packaging_action_mapping_validation_review_v1 import (
    V112CEPackagingActionMappingValidationReviewAnalyzer,
    load_json_report,
)


def test_v112ce_packaging_action_mapping_validation_runs() -> None:
    analyzer = V112CEPackagingActionMappingValidationReviewAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        bz_payload=load_json_report(Path("reports/analysis/v112bz_enabler_family_band_calibration_review_v1.json")),
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
    )
    assert result.summary["sample_count"] == 17
