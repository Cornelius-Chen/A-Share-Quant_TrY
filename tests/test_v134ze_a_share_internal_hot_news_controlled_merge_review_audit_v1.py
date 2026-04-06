from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ze_a_share_internal_hot_news_controlled_merge_review_audit_v1 import (
    V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer,
)


def test_v134ze_controlled_merge_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["combined_row_count"] > 0
    assert report.summary["merge_cluster_count"] > 0


def test_v134ze_controlled_merge_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["combined_row_count"] >= rows["merge_cluster_count"]
