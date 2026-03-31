from pathlib import Path

from a_share_quant.strategy.v112cd_packaging_role_specific_action_mapping_pilot_v1 import (
    V112CDPackagingRoleSpecificActionMappingPilotAnalyzer,
    load_json_report,
)


def test_v112cd_packaging_action_mapping_pilot_runs() -> None:
    analyzer = V112CDPackagingRoleSpecificActionMappingPilotAnalyzer()
    result = analyzer.analyze(
        bp_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        bz_payload=load_json_report(Path("reports/analysis/v112bz_enabler_family_band_calibration_review_v1.json")),
        bw_payload=load_json_report(Path("reports/analysis/v112bw_packaging_process_enabler_contrastive_control_pilot_v1.json")),
        neutral_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
    )
    assert result.summary["packaging_entry_veto_count"] == 1
    assert result.summary["packaging_eligibility_count"] == 1
