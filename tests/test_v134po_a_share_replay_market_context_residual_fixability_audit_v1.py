from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134po_a_share_replay_market_context_residual_fixability_audit_v1 import (
    V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer,
)


def test_v134po_market_context_fixability_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer(repo_root).analyze()

    assert report.summary["residual_count"] == 3
    assert report.summary["external_boundary_count"] == 2
    assert report.summary["internal_calendar_alignment_count"] == 1


def test_v134po_market_context_fixability_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134POAShareReplayMarketContextResidualFixabilityAuditV1Analyzer(repo_root).analyze()
    rows = {row["decision_trade_date"]: row for row in report.rows}

    assert rows["2023-09-22"]["fixability_class"] == "external_boundary_residual"
    assert rows["2023-12-08"]["fixability_class"] == "external_boundary_residual"
    assert rows["2026-03-28"]["fixability_class"] == "internal_calendar_alignment_candidate"
