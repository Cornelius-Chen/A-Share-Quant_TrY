from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qb_a_share_qa_shadow_execution_eligible_subset_direction_triage_v1 import (
    V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Analyzer,
)


def test_v134qb_shadow_execution_eligible_subset_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_execution_eligible_subset_is_useful_for_internal_replay_build_but_must_not_be_treated_as_execution_opening"
    )


def test_v134qb_shadow_execution_eligible_subset_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["excluded_boundary_rows"]["direction"] == (
        "retain_as_external_boundary_exclusions_and_do_not_force_internal_market_context_rebuild_for_them"
    )
