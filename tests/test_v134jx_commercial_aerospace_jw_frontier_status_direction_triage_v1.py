from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jx_commercial_aerospace_jw_frontier_status_direction_triage_v1 import (
    V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Analyzer,
)


def test_v134jx_frontier_status_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["formalized_same_plane_branch_count"] == 3
    assert report.summary["promotive_branch_count"] == 0
    assert (
        report.summary["authoritative_status"]
        == "retain_broader_attention_frontier_as_real_but_non_promotive_and_do_not_force_true_selection_from_reinforcement_only_branches"
    )


def test_v134jx_frontier_status_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JXCommercialAerospaceJWFrontierStatusDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["broader_symbol_pool_expander"] == "retain_as_logical_first_branch_but_wait_for_name_to_symbol_coverage_expansion"
    assert directions["heat_axis_and_counterpanel_expander"] == "retain_as_parallel_singleton_reinforcement_branch_only"
    assert directions["carrier_follow_search_expander"] == "retain_as_parallel_known_case_reinforcement_branch_only"
    assert directions["capital_true_selection"] == "continue_blocked_until_at_least_one_live_branch_turns_promotive"
