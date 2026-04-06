from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ma_a_share_network_fetch_adapter_foundation_audit_v1 import (
    V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer,
)


def test_v134ma_network_fetch_adapter_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["adapter_count"] == 3
    assert report.summary["host_binding_count"] > 0
    assert report.summary["stub_ready_host_count"] > 0


def test_v134ma_network_fetch_adapter_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["adapter_registry"]["component_state"] == "materialized_contracts"
    assert rows["host_binding_registry"]["component_state"] == "materialized_stub_bindings"
