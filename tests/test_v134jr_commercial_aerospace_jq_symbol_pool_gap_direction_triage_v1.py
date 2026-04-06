from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jr_commercial_aerospace_jq_symbol_pool_gap_direction_triage_v1 import (
    V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Analyzer,
)


def test_v134jr_symbol_pool_gap_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_symbol_count"] == 0
    assert (
        report.summary["authoritative_status"]
        == "treat_name_to_symbol_coverage_as_the_current_blocker_for_broader_symbol_pool_expansion_and_do_not_fake_materialization"
    )


def test_v134jr_symbol_pool_gap_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JRCommercialAerospaceJQSymbolPoolGapDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["broader_symbol_pool_expander_branch"] == "retain_as_first_live_branch_but_do_not_claim_materialized_pool"
    assert directions["local_security_master"] == "treat_as_current_materialization_blocker"
    assert directions["heat_axis_and_counterpanel_expander"] == "retain_as_next_parallel_branch_while_symbol_materialization_is_blocked"
    assert directions["capital_true_selection"] == "continue_blocked_because_broader_symbol_pool_is_not_yet_materialized"
