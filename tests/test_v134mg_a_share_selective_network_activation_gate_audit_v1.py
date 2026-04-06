from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mg_a_share_selective_network_activation_gate_audit_v1 import (
    V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer,
)


def test_v134mg_selective_network_gate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["selective_candidate_host_count"] == 20
    assert report.summary["deferred_review_only_count"] == 2
    assert report.summary["license_review_gap_present"] is True
    assert report.summary["runtime_scheduler_gap_present"] is True


def test_v134mg_selective_network_gate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer(repo_root).analyze()
    rows = {row["gate_id"]: row for row in report.rows}

    assert rows["license_review_gate"]["gate_state"] == "closed"
    assert rows["runtime_scheduler_gate"]["gate_state"] == "closed"
    assert rows["review_only_social_gate"]["gate_state"] == "deferred_review_only"
