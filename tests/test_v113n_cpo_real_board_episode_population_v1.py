from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113n_cpo_real_board_episode_population_v1 import (
    V113NCPORealBoardEpisodePopulationAnalyzer,
    load_json_report,
)


def test_v113n_cpo_real_board_episode_population() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113NCPORealBoardEpisodePopulationAnalyzer()
    result = analyzer.analyze(
        v113m_payload=load_json_report(repo_root / "reports/analysis/v113m_board_level_training_table_assembly_v1.json"),
        v112ct_payload=load_json_report(repo_root / "reports/analysis/v112ct_packaging_eligibility_admission_probe_v1.json"),
        v112cn_payload=load_json_report(repo_root / "reports/analysis/v112cn_core_leader_state_conditioned_holding_veto_probe_v1.json"),
        v112co_payload=load_json_report(repo_root / "reports/analysis/v112co_high_beta_core_derisk_probe_review_v1.json"),
        v112ci_payload=load_json_report(repo_root / "reports/analysis/v112ci_laser_maturation_probe_v1.json"),
    )

    assert result.summary["packaging_row_count"] == 2
    assert result.summary["core_leader_row_count"] == 6
    assert result.summary["high_beta_core_row_count"] == 7
    assert result.summary["laser_row_count"] == 4
    assert any(
        row["object_id"] == "core_module_leader" and row["control_label_assistant"] == "holding_veto"
        for row in result.internal_point_rows
    )
