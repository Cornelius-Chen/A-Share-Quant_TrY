from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mw_a_share_daily_market_extension_candidate_audit_v1 import (
    V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer,
)


def test_v134mw_daily_market_extension_candidate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["shadow_slice_count"] == 17
    assert report.summary["candidate_cover_count"] == 14
    assert report.summary["raw_daily_symbol_count"] == 51


def test_v134mw_daily_market_extension_candidate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MWAShareDailyMarketExtensionCandidateAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["daily_market_extension_candidate_surface"]["component_state"] == "materialized_candidate_cover_surface"
