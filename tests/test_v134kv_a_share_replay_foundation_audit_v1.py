from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kv_a_share_replay_foundation_audit_v1 import (
    V134KVAShareReplayFoundationAuditV1Analyzer,
)


def test_v134kv_replay_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KVAShareReplayFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["shadow_surface_row_count"] == 17
    assert report.summary["shadow_context_ready_count"] == 0
    assert report.summary["blocked_count"] > 0


def test_v134kv_replay_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KVAShareReplayFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["replay_component"]: row for row in report.replay_rows}

    assert rows["shadow_surface"]["component_state"] == "materialized_bootstrap"
    assert rows["shadow_replay_backlog"]["component_state"] == "backlog_materialized_not_bound_to_execution"
