from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ny_a_share_replay_promotion_latest_status_card_v1 import (
    V134NYAShareReplayPromotionLatestStatusCardV1Analyzer,
)


def test_v134ny_replay_promotion_latest_status_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NYAShareReplayPromotionLatestStatusCardV1Analyzer(repo_root).analyze()

    assert report.summary["replay_component_count"] == 6
    assert report.summary["true_source_gap_count"] == 0


def test_v134ny_replay_promotion_latest_status_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NYAShareReplayPromotionLatestStatusCardV1Analyzer(repo_root).analyze()
    rows = {row["replay_component"]: row for row in report.rows}

    assert rows["market_coverage"]["status_class"] == "external_boundary_residuals_only_under_shadow_overlay"
    assert rows["index_daily_source_horizon"]["status_class"] == "source_gap_closed"
    assert rows["paired_surfaces"]["status_class"] == "semantic_pair_layer_materialized"
    assert rows["daily_market_promotion"]["status_class"] == "promotable_subset_materialized"
    assert rows["shadow_corrected_recheck"]["status_class"] == "shadow_overlay_materialized"
