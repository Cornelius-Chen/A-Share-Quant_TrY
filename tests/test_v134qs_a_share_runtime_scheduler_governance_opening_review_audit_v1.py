from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


def test_v134qs_runtime_opening_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["review_row_count"] == 1
    assert report.summary["scheduler_pending_count"] == 1
    assert report.summary["governance_closed_count"] == 1
    assert report.summary["ready_to_open_now_count"] == 0


def test_v134qs_runtime_opening_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(repo_root).analyze()
    row = report.review_rows[0]

    assert row["adapter_id"] == "network_html_article_fetch"
    assert row["opening_review_state"] == "single_candidate_pending_scheduler_and_governance_manual_opening"
    assert row["silent_opening_allowed"] == "False"
