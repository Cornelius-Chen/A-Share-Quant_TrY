from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ms_a_share_replay_market_coverage_gap_audit_v1 import (
    V134MSAShareReplayMarketCoverageGapAuditV1Analyzer,
)


def test_v134ms_replay_market_coverage_gap_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["shadow_slice_count"] == 17
    assert report.summary["date_level_bound_count"] == 14
    assert report.summary["daily_gap_count"] == 3
    assert report.summary["intraday_present_daily_missing_count"] == 0


def test_v134ms_replay_market_coverage_gap_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MSAShareReplayMarketCoverageGapAuditV1Analyzer(repo_root).analyze()
    assert any(row["coverage_gap_state"] == "covered" for row in report.rows)
