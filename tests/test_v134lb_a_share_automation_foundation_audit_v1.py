from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lb_a_share_automation_foundation_audit_v1 import (
    V134LBAShareAutomationFoundationAuditV1Analyzer,
)


def test_v134lb_automation_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LBAShareAutomationFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["ingest_job_count"] == 3
    assert report.summary["pipeline_job_count"] == 3
    assert report.summary["review_job_count"] == 3
    assert report.summary["retention_job_count"] == 3
    assert report.summary["orchestration_flow_count"] == 2


def test_v134lb_automation_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LBAShareAutomationFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["automation_component"]: row for row in report.automation_rows}

    assert rows["retention_jobs"]["component_state"] == "materialized_bootstrap"
    assert rows["orchestration_flows"]["component_state"] == "materialized_bootstrap"
