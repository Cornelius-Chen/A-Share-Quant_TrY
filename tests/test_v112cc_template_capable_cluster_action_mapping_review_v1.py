from pathlib import Path

from a_share_quant.strategy.v112cc_template_capable_cluster_action_mapping_review_v1 import (
    V112CCTemplateCapableClusterActionMappingReviewAnalyzer,
    load_json_report,
)


def test_v112cc_action_mapping_review_runs() -> None:
    analyzer = V112CCTemplateCapableClusterActionMappingReviewAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        ca_payload=load_json_report(Path("reports/analysis/v112ca_enabler_candidate_template_promotion_split_v1.json")),
        cb_payload=load_json_report(Path("reports/analysis/v112cb_enabler_meta_cluster_abstraction_review_v1.json")),
    )
    assert result.summary["template_role_count"] == 2
    assert result.summary["eligibility_only_candidate_count"] == 1
    assert result.summary["full_three_layer_candidate_count"] == 1
