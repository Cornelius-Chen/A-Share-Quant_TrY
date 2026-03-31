from pathlib import Path

from a_share_quant.strategy.v112cf_packaging_veto_derisk_boundary_refinement_review_v1 import (
    V112CFPackagingVetoDeRiskBoundaryRefinementReviewAnalyzer,
    load_json_report,
)


def test_v112cf_packaging_boundary_refinement_runs() -> None:
    analyzer = V112CFPackagingVetoDeRiskBoundaryRefinementReviewAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        bz_payload=load_json_report(Path("reports/analysis/v112bz_enabler_family_band_calibration_review_v1.json")),
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        ce_payload=load_json_report(Path("reports/analysis/v112ce_packaging_action_mapping_validation_review_v1.json")),
    )
    assert result.summary["sample_count"] == 17
    assert result.summary["refined_action_mapping_accuracy"] > result.summary["previous_action_mapping_accuracy"]
