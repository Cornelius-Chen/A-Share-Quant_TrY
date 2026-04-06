from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mk_a_share_network_activation_operational_registry_audit_v1 import (
    V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer,
)


def test_v134mk_network_activation_operational_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer(repo_root).analyze()

    assert report.summary["license_review_row_count"] == 22
    assert report.summary["scheduler_runtime_row_count"] == 3
    assert report.summary["manual_review_pending_count"] == 20
    assert report.summary["scheduler_stub_count"] == 3


def test_v134mk_network_activation_operational_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["license_review_registry"]["component_state"] == "materialized_pending_review_surface"
    assert rows["scheduler_runtime_registry"]["component_state"] == "materialized_runtime_stub_surface"
