from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kz_a_share_governance_foundation_audit_v1 import (
    V134KZAShareGovernanceFoundationAuditV1Analyzer,
)


def test_v134kz_governance_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KZAShareGovernanceFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["schema_count"] == 11
    assert report.summary["dataset_count"] == 8
    assert report.summary["heartbeat_count"] == 13
    assert report.summary["closed_gate_count"] == 3


def test_v134kz_governance_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KZAShareGovernanceFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["governance_component"]: row for row in report.governance_rows}

    assert rows["schema_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["promotion_gates"]["component_state"] == "materialized_bootstrap"
