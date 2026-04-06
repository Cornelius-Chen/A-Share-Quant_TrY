from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lm_a_share_limit_halt_foundation_audit_v1 import (
    V134LMAShareLimitHaltFoundationAuditV1Analyzer,
)


def test_v134lm_limit_halt_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LMAShareLimitHaltFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["surface_row_count"] == 1936
    assert report.summary["residual_count"] == 3
    assert report.summary["limit_up_hit_count"] >= 0


def test_v134lm_limit_halt_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LMAShareLimitHaltFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["limit_halt_surface"]["component_state"] == "materialized_bootstrap"
    assert rows["limit_halt_residual_backlog"]["component_state"] == "materialized_named_residuals"
