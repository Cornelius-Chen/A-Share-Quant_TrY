from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134md_a_share_mc_network_fetch_activation_direction_triage_v1 import (
    V134MDAShareMCNetworkFetchActivationDirectionTriageV1Analyzer,
)


def test_v134md_network_fetch_activation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MDAShareMCNetworkFetchActivationDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "network_fetch_activation_policy_complete_enough_to_freeze_until_selective_activation_shift"
    )


def test_v134md_network_fetch_activation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MDAShareMCNetworkFetchActivationDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["network_fetch_activation_policy"]["direction"].startswith("freeze_policy_retry")
    assert rows["next_frontier"]["direction"].startswith("selectively_activate_licensed_T2_T3_hosts")
