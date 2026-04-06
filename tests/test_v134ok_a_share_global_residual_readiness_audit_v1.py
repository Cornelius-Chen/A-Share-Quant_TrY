from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ok_a_share_global_residual_readiness_audit_v1 import (
    V134OKAShareGlobalResidualReadinessAuditV1Analyzer,
)


def test_v134ok_global_residual_readiness_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OKAShareGlobalResidualReadinessAuditV1Analyzer(repo_root).analyze()

    assert report.summary["backlog_group_count"] == 5
    assert report.summary["internally_actionable_group_count"] == 2
    assert report.summary["externally_dependent_group_count"] == 1


def test_v134ok_global_residual_readiness_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OKAShareGlobalResidualReadinessAuditV1Analyzer(repo_root).analyze()
    rows = {row["backlog_group"]: row for row in report.rows}

    assert rows["source_internal_manual"]["readiness_state"] == "workpack_ready_manual_fill_pending"
    assert rows["replay_external_source"]["readiness_state"] == "deferred_prelaunch_closed"
