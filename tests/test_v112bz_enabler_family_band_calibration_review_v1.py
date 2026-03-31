from pathlib import Path

from a_share_quant.strategy.v112bz_enabler_family_band_calibration_review_v1 import (
    V112BZEnablerFamilyBandCalibrationReviewAnalyzer,
    load_json_report,
)


def test_v112bz_calibration_review_runs() -> None:
    analyzer = V112BZEnablerFamilyBandCalibrationReviewAnalyzer()
    result = analyzer.analyze(
        bx_payload=load_json_report(Path("reports/analysis/v112bx_packaging_process_enabler_balance_band_review_v1.json")),
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        az_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
    )
    assert result.summary["role_count"] == 3
