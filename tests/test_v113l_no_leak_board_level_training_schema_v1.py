from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113l_no_leak_board_level_training_schema_v1 import (
    V113LNoLeakBoardLevelTrainingSchemaAnalyzer,
    load_json_report,
)


def test_v113l_no_leak_board_level_training_schema() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113LNoLeakBoardLevelTrainingSchemaAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(repo_root / "reports/analysis/v113i_board_level_owner_labeling_protocol_v1.json"),
        v113j_payload=load_json_report(repo_root / "reports/analysis/v113j_board_research_world_model_protocol_v1.json"),
        v113k_payload=load_json_report(repo_root / "reports/analysis/v113k_cpo_world_model_asset_mapping_v1.json"),
    )

    assert result.summary["training_unit"] == "board_state_episode_with_cross_sectional_internal_points"
    assert result.summary["split_policy"] == "time_or_cycle_only"
    assert result.summary["allowed_group_count"] == 4
    assert result.summary["blocked_group_count"] == 4
