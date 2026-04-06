from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nq_a_share_runtime_candidate_dependency_audit_v1 import (
    V134NQAShareRuntimeCandidateDependencyAuditV1Analyzer,
)


def test_v134nq_runtime_candidate_dependency_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NQAShareRuntimeCandidateDependencyAuditV1Analyzer(repo_root).analyze()

    assert report.summary["runtime_row_count"] == 3
    assert report.summary["promotable_now_count"] == 0
    assert report.summary["pending_batch_one_count"] == 0


def test_v134nq_runtime_candidate_dependency_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NQAShareRuntimeCandidateDependencyAuditV1Analyzer(repo_root).analyze()
    rows = {row["adapter_id"]: row for row in report.rows}

    assert rows["network_html_article_fetch"]["dependency_state"] == "manual_batch_one_cleared_pending_runtime_scheduler"
    assert rows["network_social_column_fetch"]["dependency_state"] == "review_only_nonpromotive"
