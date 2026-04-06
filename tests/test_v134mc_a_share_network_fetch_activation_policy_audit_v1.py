from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mc_a_share_network_fetch_activation_policy_audit_v1 import (
    V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer,
)


def test_v134mc_network_fetch_activation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer(repo_root).analyze()

    assert report.summary["adapter_policy_count"] == 3
    assert report.summary["retry_policy_count"] == 3
    assert report.summary["host_binding_count"] > 0
    assert report.summary["selective_candidate_host_count"] > 0


def test_v134mc_network_fetch_activation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["adapter_policy_registry"]["component_state"] == "materialized_policy_bindings"
    assert rows["retry_policy_registry"]["component_state"] == "materialized_retry_bindings"
    assert rows["orchestration_binding_registry"]["component_state"] == "materialized_host_bindings"
