from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lo_a_share_source_activation_foundation_audit_v1 import (
    V134LOAShareSourceActivationFoundationAuditV1Analyzer,
)


def test_v134lo_source_activation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LOAShareSourceActivationFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["active_local_ingest_count"] == 7
    assert report.summary["historical_url_catalog_count"] > 0
    assert report.summary["locally_activatable_job_count"] == 3


def test_v134lo_source_activation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LOAShareSourceActivationFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["source_activation_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["source_activation_residual_backlog"]["component_state"] == "materialized_named_residuals"
