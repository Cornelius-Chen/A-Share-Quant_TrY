from pathlib import Path

from a_share_quant.strategy.v112ca_enabler_candidate_template_promotion_split_v1 import (
    V112CAEnablerCandidateTemplatePromotionSplitAnalyzer,
    load_json_report,
)


def test_v112ca_promotion_split_runs() -> None:
    analyzer = V112CAEnablerCandidateTemplatePromotionSplitAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        bz_payload=load_json_report(Path("reports/analysis/v112bz_enabler_family_band_calibration_review_v1.json")),
    )
    assert result.summary["role_count"] == 3
    assert result.summary["candidate_template_path_count"] == 1
    assert result.summary["role_specific_template_count"] == 1
    assert result.summary["isolated_diagnostic_path_count"] == 1
