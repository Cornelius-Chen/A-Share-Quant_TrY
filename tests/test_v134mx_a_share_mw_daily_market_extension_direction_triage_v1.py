from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mx_a_share_mw_daily_market_extension_direction_triage_v1 import (
    V134MXAShareMWDailyMarketExtensionDirectionTriageV1Analyzer,
)


def test_v134mx_daily_market_extension_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MXAShareMWDailyMarketExtensionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "daily_market_extension_candidate_ready_for_controlled_promotion_review"
    )


def test_v134mx_daily_market_extension_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MXAShareMWDailyMarketExtensionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["daily_market_extension_candidate_surface"]["direction"].startswith("review_and_promote_candidate_daily_rows")
