from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mh_a_share_mg_selective_network_direction_triage_v1 import (
    V134MHAShareMGSelectiveNetworkDirectionTriageV1Analyzer,
)


def test_v134mh_selective_network_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MHAShareMGSelectiveNetworkDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "selective_network_activation_kept_closed_until_license_and_scheduler_gates_open"
    )


def test_v134mh_selective_network_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MHAShareMGSelectiveNetworkDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["license_review_gate"]["direction"].startswith("resolve_host_allowlist")
    assert rows["runtime_scheduler_gate"]["direction"].startswith("bind_policy_bound_adapters")
