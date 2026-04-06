from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mz_a_share_my_daily_market_promotion_direction_triage_v1 import (
    V134MZAShareMYDailyMarketPromotionDirectionTriageV1Analyzer,
)


def test_v134mz_daily_market_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MZAShareMYDailyMarketPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "daily_market_promotion_reopened_with_promotable_subset_after_semantic_pair_materialization"
    )


def test_v134mz_daily_market_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MZAShareMYDailyMarketPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["paired_surfaces"]["direction"].startswith("retire_old_pair-gap_language")
