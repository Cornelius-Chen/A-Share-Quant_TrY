from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v112cx_core_leader_holding_veto_promotion_review_v1 import (
    V112CXCoreLeaderHoldingVetoPromotionReviewAnalyzer,
    load_json_report,
)


def test_v112cx_core_leader_holding_veto_promotion_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V112CXCoreLeaderHoldingVetoPromotionReviewAnalyzer()
    result = analyzer.analyze(
        cn_payload=load_json_report(repo_root / "reports/analysis/v112cn_core_leader_state_conditioned_holding_veto_probe_v1.json"),
        cw_payload=load_json_report(repo_root / "reports/analysis/v112cw_packaging_mainline_extension_status_freeze_v1.json"),
        cs_payload=load_json_report(repo_root / "reports/analysis/v112cs_core_residual_stack_status_freeze_v1.json"),
    )
    summary = result.summary
    assert summary["promotion_ready"] is True
    assert summary["promotion_posture"] == "core_residual_promotable_holding_veto_candidate"
    row = result.promotion_rows[0]
    assert row["beats_neutral_return"] is True
    assert row["beats_neutral_drawdown"] is True
