from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134og_a_share_batch_one_manual_review_workpack_audit_v1 import (
    V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer,
)


def test_v134og_manual_review_workpack_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer(repo_root).analyze()

    assert report.summary["workpack_row_count"] == 4
    assert report.summary["host_count"] == 4


def test_v134og_manual_review_workpack_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer(repo_root).analyze()
    rows = {row["host"]: row for row in report.workpack_rows}

    assert "https://" in rows["finance.sina.com.cn"]["source_urls"]
    assert rows["finance.sina.com.cn"]["manual_license_outcome"] == "pending"
