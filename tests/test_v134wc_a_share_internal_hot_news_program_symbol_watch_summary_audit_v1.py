from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134wc_a_share_internal_hot_news_program_symbol_watch_summary_audit_v1 import (
    V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer,
)


def test_v134wc_program_symbol_watch_summary_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer(repo_root).analyze()

    assert report.summary["summary_row_count"] == 1
    assert report.summary["watchlist_row_count"] >= 0
    assert report.summary["top_watch_mapping_confidence"] in {"unknown", "low", "medium", "high"}


def test_v134wc_program_symbol_watch_summary_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WCAShareInternalHotNewsProgramSymbolWatchSummaryAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_symbol_watch_summary"] == "read_ready_internal_only"
    assert rows["watchlist_coverage"] == "materialized"
