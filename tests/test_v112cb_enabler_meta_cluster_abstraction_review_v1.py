from pathlib import Path

from a_share_quant.strategy.v112cb_enabler_meta_cluster_abstraction_review_v1 import (
    V112CBEnablerMetaClusterAbstractionReviewAnalyzer,
    load_json_report,
)


def test_v112cb_meta_cluster_abstraction_runs() -> None:
    analyzer = V112CBEnablerMetaClusterAbstractionReviewAnalyzer()
    result = analyzer.analyze(
        by_payload=load_json_report(Path("reports/analysis/v112by_enabler_family_balance_band_transfer_probe_v1.json")),
        ca_payload=load_json_report(Path("reports/analysis/v112ca_enabler_candidate_template_promotion_split_v1.json")),
    )
    assert result.summary["role_count"] == 3
    assert result.summary["meta_cluster_count"] == 2
    assert result.summary["template_capable_cluster_count"] == 1
    assert result.summary["diagnostic_cluster_count"] == 1
