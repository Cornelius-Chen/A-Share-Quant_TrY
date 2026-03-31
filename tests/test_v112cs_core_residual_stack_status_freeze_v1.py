from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cs_core_residual_stack_status_freeze_v1 import (
    V112CSCoreResidualStackStatusFreezeAnalyzer,
    load_json_report,
)


def test_v112cs_core_residual_stack_status_freeze() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CSCoreResidualStackStatusFreezeAnalyzer()
    result = analyzer.analyze(
        ch_payload=load_json_report(repo_root / "reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json"),
        ci_payload=load_json_report(repo_root / "reports/analysis/v112ci_laser_maturation_probe_v1.json"),
        cn_payload=load_json_report(repo_root / "reports/analysis/v112cn_core_leader_state_conditioned_holding_veto_probe_v1.json"),
        cq_payload=load_json_report(repo_root / "reports/analysis/v112cq_high_beta_core_derisk_calibration_refinement_review_v1.json"),
        cr_payload=load_json_report(repo_root / "reports/analysis/v112cr_high_beta_core_derisk_replay_split_v1.json"),
    )
    summary = result.summary
    assert summary["mainline_asset_count"] == 1
    assert summary["core_residual_candidate_count"] == 1
    assert summary["core_residual_sidecar_count"] == 1
    assert summary["joint_promotion_ready"] is False
