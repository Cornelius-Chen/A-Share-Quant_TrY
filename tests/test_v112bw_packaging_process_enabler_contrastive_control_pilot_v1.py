from pathlib import Path

from a_share_quant.strategy.v112bw_packaging_process_enabler_contrastive_control_pilot_v1 import (
    V112BWPackagingProcessEnablerContrastiveControlPilotAnalyzer,
    load_json_report,
)


def test_v112bw_contrastive_control_pilot_runs() -> None:
    analyzer = V112BWPackagingProcessEnablerContrastiveControlPilotAnalyzer()
    result = analyzer.analyze(
        bp_fusion_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        bt_extraction_payload=load_json_report(Path("reports/analysis/v112bt_phase_conditioned_veto_and_eligibility_extraction_v1.json")),
        bv_control_pilot_payload=load_json_report(Path("reports/analysis/v112bv_contributor_aligned_control_pilot_v1.json")),
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
    )
    assert result.summary["contrastive_veto_count"] >= 1
