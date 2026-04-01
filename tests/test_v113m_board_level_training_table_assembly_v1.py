from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113m_board_level_training_table_assembly_v1 import (
    V113MBoardLevelTrainingTableAssemblyAnalyzer,
    load_json_report,
)


def test_v113m_board_level_training_table_assembly() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113MBoardLevelTrainingTableAssemblyAnalyzer()
    result = analyzer.analyze(
        v113i_payload=load_json_report(repo_root / "reports/analysis/v113i_board_level_owner_labeling_protocol_v1.json"),
        v113k_payload=load_json_report(repo_root / "reports/analysis/v113k_cpo_world_model_asset_mapping_v1.json"),
        v113l_payload=load_json_report(repo_root / "reports/analysis/v113l_no_leak_board_level_training_schema_v1.json"),
    )

    assert result.summary["training_unit"] == "board_state_episode_with_cross_sectional_internal_points"
    assert result.summary["table_count"] == 3
    assert result.summary["sample_episode_count"] == 5
    assert any(
        row["object_id"] == "packaging_process_enabler" and row["control_label_assistant"] == "eligibility"
        for row in result.sample_episode_rows
    )
