from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oe_a_share_information_center_global_residual_backlog_audit_v1 import (
    V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer,
)


def test_v134oe_global_residual_backlog_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer(repo_root).analyze()

    assert report.summary["backlog_count"] == 6
    assert report.summary["source_runtime_count"] == 1
    assert report.summary["external_source_count"] == 2


def test_v134oe_global_residual_backlog_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OEAShareInformationCenterGlobalResidualBacklogAuditV1Analyzer(repo_root).analyze()
    rows = {row["backlog_id"]: row for row in report.backlog_rows}

    assert rows["bg_001"]["backlog_group"] == "source_runtime_followthrough"
    assert rows["bg_001"]["backlog_item"] == "runtime_scheduler_governance_opening_followthrough_for_html_article_fetch"
    assert rows["bg_003"]["backlog_group"] == "replay_external_source"
