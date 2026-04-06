from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nk_a_share_batch_one_allowlist_review_surface_audit_v1 import (
    V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer,
)


def test_v134nk_batch_one_allowlist_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["batch_one_source_count"] == 6
    assert report.summary["host_review_unit_count"] == 4
    assert report.summary["promotable_now_count"] == 0


def test_v134nk_batch_one_allowlist_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["host"]: row for row in report.review_rows}

    assert rows["finance.sina.com.cn"]["review_mode"] == "primary_batch_one_host_family_review"
    assert rows["stock.finance.sina.com.cn"]["review_mode"] == "sibling_host_review_after_primary_sina_family"
