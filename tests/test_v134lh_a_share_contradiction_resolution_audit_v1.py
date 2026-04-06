from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lh_a_share_contradiction_resolution_audit_v1 import (
    V134LHAShareContradictionResolutionAuditV1Analyzer,
)


def test_v134lh_contradiction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LHAShareContradictionResolutionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["registry_group_count"] > 0
    assert report.summary["duplicate_merge_candidate_count"] > 0
    assert report.summary["semantic_divergence_count"] >= 0


def test_v134lh_contradiction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LHAShareContradictionResolutionAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["contradiction_graph"]["component_state"] == "materialized_bootstrap"
    assert rows["residual_backlog"]["component_state"] == "materialized_named_residuals"
