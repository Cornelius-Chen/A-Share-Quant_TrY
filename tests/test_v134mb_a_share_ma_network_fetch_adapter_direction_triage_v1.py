from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mb_a_share_ma_network_fetch_adapter_direction_triage_v1 import (
    V134MBAShareMANetworkFetchAdapterDirectionTriageV1Analyzer,
)


def test_v134mb_network_fetch_adapter_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MBAShareMANetworkFetchAdapterDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["adapter_count"] == 3
    assert (
        report.summary["authoritative_status"]
        == "network_fetch_adapter_foundation_complete_enough_to_freeze_as_scaffold"
    )


def test_v134mb_network_fetch_adapter_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MBAShareMANetworkFetchAdapterDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "bind_selected_adapters_to_orchestration_license_review_and_retry_policy_before_activation"
    )
