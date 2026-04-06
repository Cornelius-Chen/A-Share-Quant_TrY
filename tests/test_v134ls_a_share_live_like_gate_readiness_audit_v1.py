from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ls_a_share_live_like_gate_readiness_audit_v1 import (
    V134LSAShareLiveLikeGateReadinessAuditV1Analyzer,
)


def test_v134ls_live_like_readiness_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LSAShareLiveLikeGateReadinessAuditV1Analyzer(repo_root).analyze()

    assert report.summary["active_local_ingest_count"] == 7
    assert report.summary["active_review_queue_count"] == 3
    assert report.summary["materialized_live_like_view_count"] == 2
    assert report.summary["live_like_ready_now"] is False


def test_v134ls_live_like_readiness_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LSAShareLiveLikeGateReadinessAuditV1Analyzer(repo_root).analyze()
    rows = {row["gate_component"]: row for row in report.rows}

    assert rows["governance_gates"]["component_state"] == "closed"
    assert rows["serving_live_like"]["component_state"] == "materialized_but_blocked"
