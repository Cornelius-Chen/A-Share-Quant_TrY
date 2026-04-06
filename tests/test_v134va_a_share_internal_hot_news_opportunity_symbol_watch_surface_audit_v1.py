from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134va_a_share_internal_hot_news_opportunity_symbol_watch_surface_audit_v1 import (
    V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer,
)


def test_v134va_opportunity_symbol_watch_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["symbol_watch_row_count"] >= 0
    assert report.summary["unique_symbol_count"] >= 0
    assert report.summary["opportunity_event_count"] >= 0


def test_v134va_opportunity_symbol_watch_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VAAShareInternalHotNewsOpportunitySymbolWatchSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["opportunity_symbol_watch_surface"] == "read_ready_internal_only"
    assert rows["unique_symbols"] == "materialized"
