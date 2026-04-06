from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ml_a_share_mk_network_activation_operational_direction_triage_v1 import (
    V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Analyzer,
)


def test_v134ml_network_activation_operational_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "network_activation_operations_ready_for_queue_processing_but_not_activation"
    )


def test_v134ml_network_activation_operational_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["license_review_registry"]["direction"].startswith("process_allowlist_decisions")
