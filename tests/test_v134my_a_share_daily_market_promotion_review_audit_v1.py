from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134my_a_share_daily_market_promotion_review_audit_v1 import (
    V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer,
)


def test_v134my_daily_market_promotion_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["review_row_count"] == 17
    assert report.summary["promotable_now_count"] == 14
    assert report.summary["blocked_by_paired_surface_count"] == 0
    assert report.summary["blocked_no_candidate_count"] == 3


def test_v134my_daily_market_promotion_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MYAShareDailyMarketPromotionReviewAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert (
        rows["daily_market_promotion_review"]["component_state"]
        == "materialized_controlled_review_surface_with_promotable_subset"
    )
