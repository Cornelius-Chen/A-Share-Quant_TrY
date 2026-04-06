from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ns_a_share_batch_one_manual_review_record_surface_audit_v1 import (
    V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer,
)


def test_v134ns_manual_review_record_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["record_row_count"] == 4
    assert report.summary["pending_record_count"] == 0
    assert report.summary["completed_record_count"] == 4


def test_v134ns_manual_review_record_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer(repo_root).analyze()
    first_row = report.record_rows[0]

    assert first_row["license_terms_checked"] == "checked"
    assert first_row["record_state"] == "manual_review_completed"
