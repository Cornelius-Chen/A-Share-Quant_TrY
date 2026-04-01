from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113q_cpo_training_material_readiness_audit_v1 import (
    V113QCPOTrainingMaterialReadinessAuditAnalyzer,
    load_json_report,
)


def test_v113q_cpo_training_material_readiness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113QCPOTrainingMaterialReadinessAuditAnalyzer()
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113p_payload=load_json_report(repo_root / "reports" / "analysis" / "v113p_cpo_full_board_coverage_and_t1_audit_v1.json"),
    )

    assert result.summary["time_order_ready"] is True
    assert result.summary["full_board_information_complete"] is False
    assert result.summary["full_board_training_ready_now"] is False
    assert result.summary["subset_training_ready_now"] is True
