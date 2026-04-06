from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mn_a_share_mm_network_activation_queue_direction_triage_v1 import (
    V134MNAShareMMNetworkActivationQueueDirectionTriageV1Analyzer,
)


def test_v134mn_network_activation_queue_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MNAShareMMNetworkActivationQueueDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "network_activation_queue_surface_complete_enough_to_freeze_until_queue_processing"
    )


def test_v134mn_network_activation_queue_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MNAShareMMNetworkActivationQueueDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["allowlist_decision_queue"]["direction"].startswith("process_license_terms")
