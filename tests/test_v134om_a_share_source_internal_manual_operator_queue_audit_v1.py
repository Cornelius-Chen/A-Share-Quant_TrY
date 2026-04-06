from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134om_a_share_source_internal_manual_operator_queue_audit_v1 import (
    V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer,
)


def test_v134om_source_internal_manual_operator_queue_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer(repo_root).analyze()

    assert report.summary["queue_row_count"] == 4
    assert report.summary["manual_review_completed_count"] == 4
    assert report.summary["ready_primary_review_count"] == 0
    assert report.summary["dependency_blocked_count"] == 0


def test_v134om_source_internal_manual_operator_queue_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer(repo_root).analyze()
    rows = {row["host"]: row for row in report.queue_rows}

    assert rows["finance.sina.com.cn"]["dependency_state"] == "primary_review_completed"
    assert rows["stock.finance.sina.com.cn"]["dependency_state"] == "sibling_review_completed"
