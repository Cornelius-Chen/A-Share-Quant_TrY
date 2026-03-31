from pathlib import Path

from a_share_quant.strategy.v112cg_packaging_refined_action_mapping_pilot_v1 import (
    V112CGPackagingRefinedActionMappingPilotAnalyzer,
    load_json_report,
)


def test_v112cg_packaging_refined_pilot_runs() -> None:
    analyzer = V112CGPackagingRefinedActionMappingPilotAnalyzer()
    result = analyzer.analyze(
        cd_payload=load_json_report(Path("reports/analysis/v112cd_packaging_role_specific_action_mapping_pilot_v1.json")),
        cf_payload=load_json_report(Path("reports/analysis/v112cf_packaging_veto_derisk_boundary_refinement_review_v1.json")),
    )
    assert result.summary["realized_path_changed"] is False
