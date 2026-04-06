from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nm_a_share_batch_one_allowlist_decision_surface_audit_v1 import (
    V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer,
)


def test_v134nm_batch_one_decision_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["decision_unit_count"] == 4
    assert report.summary["pending_manual_decision_count"] == 0
    assert report.summary["manually_approved_count"] == 4
    assert report.summary["promotable_now_count"] == 0


def test_v134nm_batch_one_decision_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["host"]: row for row in report.decision_rows}

    assert rows["finance.sina.com.cn"]["review_priority_order"] == 1
    assert rows["finance.sina.com.cn"]["manual_license_decision"] == "allow"
    assert rows["stock.finance.sina.com.cn"]["recommended_review_gate"] == "review_after_primary_host_family_outcome"
