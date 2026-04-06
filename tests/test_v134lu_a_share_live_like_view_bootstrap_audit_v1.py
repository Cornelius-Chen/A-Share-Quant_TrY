from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lu_a_share_live_like_view_bootstrap_audit_v1 import (
    V134LUAShareLiveLikeViewBootstrapAuditV1Analyzer,
)


def test_v134lu_live_like_view_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LUAShareLiveLikeViewBootstrapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["event_state_row_count"] == 17
    assert report.summary["closed_gate_count"] == 3
    assert report.summary["candidate_context_blocked_count"] >= 1


def test_v134lu_live_like_view_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LUAShareLiveLikeViewBootstrapAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["live_like_view_registry"]["component_state"] == "materialized_but_blocked"
    assert rows["live_like_gate_view"]["component_state"] == "materialized_but_blocked"
