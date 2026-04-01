from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113k_cpo_world_model_asset_mapping_v1 import (
    V113KCPOWorldModelAssetMappingAnalyzer,
    load_json_report,
)


def test_v113k_cpo_world_model_asset_mapping() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113KCPOWorldModelAssetMappingAnalyzer()
    result = analyzer.analyze(
        v113j_payload=load_json_report(repo_root / "reports/analysis/v113j_board_research_world_model_protocol_v1.json"),
        v112cw_payload=load_json_report(repo_root / "reports/analysis/v112cw_packaging_mainline_extension_status_freeze_v1.json"),
        v112cx_payload=load_json_report(repo_root / "reports/analysis/v112cx_core_leader_holding_veto_promotion_review_v1.json"),
        v112cs_payload=load_json_report(repo_root / "reports/analysis/v112cs_core_residual_stack_status_freeze_v1.json"),
    )

    assert result.summary["board_name"] == "CPO"
    assert result.summary["object_count"] == 6
    assert result.summary["relation_count"] == 5
    assert result.summary["transition_count"] == 4
    assert result.summary["constraint_count"] == 4
