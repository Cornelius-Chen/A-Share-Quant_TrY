from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mm_a_share_network_activation_queue_surface_audit_v1 import (
    V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer,
)


def test_v134mm_network_activation_queue_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["allowlist_queue_count"] == 20
    assert report.summary["runtime_queue_count"] == 3


def test_v134mm_network_activation_queue_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["allowlist_decision_queue"]["component_state"] == "materialized_pending_queue"
    assert rows["runtime_deployment_queue"]["component_state"] == "materialized_pending_queue"
