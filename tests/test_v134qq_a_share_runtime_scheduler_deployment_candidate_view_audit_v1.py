from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qq_a_share_runtime_scheduler_deployment_candidate_view_audit_v1 import (
    V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer,
)


def test_v134qq_runtime_deployment_candidate_view_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_row_count"] == 1
    assert report.summary["promotable_now_count"] == 0


def test_v134qq_runtime_deployment_candidate_view_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer(repo_root).analyze()
    row = report.candidate_rows[0]

    assert row["adapter_id"] == "network_html_article_fetch"
    assert row["deployment_candidate_state"] == "single_candidate_pending_governance_and_scheduler_opening"

