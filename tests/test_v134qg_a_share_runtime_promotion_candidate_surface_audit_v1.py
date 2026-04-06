from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qg_a_share_runtime_promotion_candidate_surface_audit_v1 import (
    V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer,
)


def test_v134qg_runtime_promotion_candidate_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["runtime_row_count"] == 3
    assert report.summary["priority_runtime_candidate_count"] == 1
    assert report.summary["excluded_runtime_row_count"] == 2
    assert report.summary["promotable_now_count"] == 0


def test_v134qg_runtime_promotion_candidate_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["adapter_id"]: row for row in report.rows}

    assert rows["network_html_article_fetch"]["candidate_class"] == "priority_runtime_candidate"
    assert rows["network_html_article_fetch"]["candidate_state"] == "manual_review_cleared_pending_scheduler_activation"
    assert rows["network_social_column_fetch"]["excluded_from_first_runtime_lane"] == "True"

