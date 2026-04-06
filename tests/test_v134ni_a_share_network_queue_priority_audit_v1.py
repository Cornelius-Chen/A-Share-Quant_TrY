from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ni_a_share_network_queue_priority_audit_v1 import (
    V134NIAShareNetworkQueuePriorityAuditV1Analyzer,
)


def test_v134ni_network_queue_priority_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NIAShareNetworkQueuePriorityAuditV1Analyzer(repo_root).analyze()

    assert report.summary["allowlist_row_count"] == 20
    assert report.summary["runtime_row_count"] == 3
    assert report.summary["allowlist_batch_one_count"] > 0


def test_v134ni_network_queue_priority_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NIAShareNetworkQueuePriorityAuditV1Analyzer(repo_root).analyze()

    assert any(row["queue_priority"] == "batch_one_manual_license_review" for row in report.allowlist_rows)
    assert any(row["queue_priority"] == "deferred_manual_review" for row in report.allowlist_rows)
    assert any(
        row["queue_priority"] == "first_runtime_candidate_after_batch_one_allowlist" for row in report.runtime_rows
    )
