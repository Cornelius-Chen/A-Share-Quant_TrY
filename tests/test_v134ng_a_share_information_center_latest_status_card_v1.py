from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ng_a_share_information_center_latest_status_card_v1 import (
    V134NGAShareInformationCenterLatestStatusCardV1Analyzer,
)


def test_v134ng_latest_status_card_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NGAShareInformationCenterLatestStatusCardV1Analyzer(repo_root).analyze()

    assert report.summary["foundation_complete_count"] == 13
    assert report.summary["workstream_count"] == 13
    assert report.summary["true_source_gap_count"] == 0


def test_v134ng_latest_status_card_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NGAShareInformationCenterLatestStatusCardV1Analyzer(repo_root).analyze()
    rows = {row["status_component"]: row for row in report.rows}

    assert rows["source_activation_queue_surface"]["status_class"] == "single_runtime_opening_review_stopline"
    assert rows["index_daily_source_horizon"]["status_class"] == "source_gap_closed"
    assert rows["daily_market_promotion"]["status_class"] == "promotable_subset_materialized"
    assert rows["limit_halt_derivation"]["status_class"] == "semantic_surface_materialized_for_recheck"
    assert rows["market_context_residuals"]["status_class"] == "external_boundary_residuals_only_under_shadow_overlay"
    assert rows["execution_live_like_gate_stack"]["status_class"] == "explicitly_blocked"
