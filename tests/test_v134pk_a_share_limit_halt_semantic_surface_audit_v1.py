from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pk_a_share_limit_halt_semantic_surface_audit_v1 import (
    V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer,
)


def test_v134pk_limit_halt_semantic_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["symbol_count"] == 51
    assert report.summary["coverage_start"] == "20240102"
    assert report.summary["coverage_end"] == "20260403"


def test_v134pk_limit_halt_semantic_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["limit_halt_semantic_surface"]["component_state"] == "materialized_semantic_replay_surface"
