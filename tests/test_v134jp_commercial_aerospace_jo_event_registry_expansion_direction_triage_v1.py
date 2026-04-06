from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jp_commercial_aerospace_jo_event_registry_expansion_direction_triage_v1 import (
    V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Analyzer,
)


def test_v134jp_decisive_registry_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["retained_registry_row_count"] == 12
    assert report.summary["broader_symbol_pool_expander_count"] == 4
    assert report.summary["capital_true_selection_blocked"] is True
    assert (
        report.summary["authoritative_status"]
        == "treat_broader_symbol_pool_expansion_from_the_decisive_registry_as_the_first_live_same_plane_branch_and_keep_true_selection_blocked"
    )


def test_v134jp_decisive_registry_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JPCommercialAerospaceJOEventRegistryExpansionDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["broader_symbol_pool_expander"] == "promote_as_first_decisive_registry_symbol_expansion_branch"
    assert directions["heat_axis_and_counterpanel_expander"] == "retain_as_second_decisive_registry_expansion_branch"
    assert directions["carrier_follow_search_expander"] == "retain_as_parallel_registry_branch_for_future_carrier_support"
    assert directions["event_context_alignment_and_risk_anchors"] == "retain_as_environment_alignment_support_only"
    assert directions["capital_true_selection"] == "continue_blocked_during_registry_expansion_stage"
