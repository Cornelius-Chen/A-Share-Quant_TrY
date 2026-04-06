from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oc_a_share_information_center_global_blocker_status_card_v1 import (
    V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer,
)


def test_v134oc_global_blocker_status_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer(repo_root).analyze()

    assert report.summary["global_component_count"] == 7
    assert report.summary["source_blocker_count"] == 1
    assert report.summary["replay_true_source_gap_count"] == 0


def test_v134oc_global_blocker_status_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OCAShareInformationCenterGlobalBlockerStatusCardV1Analyzer(repo_root).analyze()
    rows = {row["global_component"]: row for row in report.rows}

    assert rows["source_side_closure"]["global_state"] == "single_runtime_opening_review_lane_pending_scheduler_and_governance_movement"
    assert rows["index_daily_extension_frontier"]["global_state"] == "opened_for_downstream_reaudit"
    assert rows["replay_promotion"]["global_state"] == "promotable_subset_materialized"
    assert rows["limit_halt_derivation_frontier"]["global_state"] == "semantic_materialization_complete_for_recheck"
    assert rows["market_context_residual_frontier"]["global_state"] == "external_boundary_residuals_only_under_shadow_overlay"
