from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lw_a_share_execution_binding_blocker_stack_audit_v1 import (
    V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer,
)


def test_v134lw_execution_binding_blocker_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer(repo_root).analyze()

    assert report.summary["blocker_count"] == 6
    assert report.summary["governance_blocker_count"] == 2
    assert report.summary["replay_blocker_count"] == 2


def test_v134lw_execution_binding_blocker_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LWAShareExecutionBindingBlockerStackAuditV1Analyzer(repo_root).analyze()

    assert any(row["blocker_id"] == "network_fetch_binding_gap" for row in report.blocker_rows)
