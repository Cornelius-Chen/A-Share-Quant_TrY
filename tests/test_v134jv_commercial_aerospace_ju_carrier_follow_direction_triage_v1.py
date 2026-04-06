from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jv_commercial_aerospace_ju_carrier_follow_direction_triage_v1 import (
    V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Analyzer,
)


def test_v134jv_carrier_follow_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["linked_local_case_count"] == 2
    assert report.summary["outside_named_watch_count"] == 1
    assert report.summary["branch_promotive"] is False
    assert (
        report.summary["authoritative_status"]
        == "treat_carrier_follow_search_as_formalized_same_plane_reinforcement_and_keep_true_selection_blocked"
    )


def test_v134jv_carrier_follow_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JVCommercialAerospaceJUCarrierFollowDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["linked_carrier_case"] == "retain_as_same_plane_carrier_reinforcement_only"
    assert directions["linked_follow_case"] == "retain_as_same_plane_follow_reinforcement_only"
    assert directions["outside_named_supply_chain_watch"] == "retain_as_future_watch_without_symbol_promotion"
    assert directions["capital_true_selection"] == "continue_blocked_while_branch_remains_reinforcement_only"
