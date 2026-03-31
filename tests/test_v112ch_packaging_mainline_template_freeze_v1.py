from pathlib import Path

from a_share_quant.strategy.v112ch_packaging_mainline_template_freeze_v1 import (
    V112CHPackagingMainlineTemplateFreezeAnalyzer,
    load_json_report,
)


def test_v112ch_packaging_mainline_template_freeze_runs() -> None:
    analyzer = V112CHPackagingMainlineTemplateFreezeAnalyzer()
    result = analyzer.analyze(
        cc_payload=load_json_report(Path("reports/analysis/v112cc_template_capable_cluster_action_mapping_review_v1.json")),
        cd_payload=load_json_report(Path("reports/analysis/v112cd_packaging_role_specific_action_mapping_pilot_v1.json")),
        cf_payload=load_json_report(Path("reports/analysis/v112cf_packaging_veto_derisk_boundary_refinement_review_v1.json")),
        cg_payload=load_json_report(Path("reports/analysis/v112cg_packaging_refined_action_mapping_pilot_v1.json")),
    )
    assert result.summary["cluster_mainline_template_asset_count"] == 1
