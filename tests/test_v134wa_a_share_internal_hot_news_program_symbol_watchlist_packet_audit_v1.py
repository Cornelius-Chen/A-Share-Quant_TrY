from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134wa_a_share_internal_hot_news_program_symbol_watchlist_packet_audit_v1 import (
    V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer,
)


def test_v134wa_program_symbol_watchlist_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["watchlist_row_count"] >= 0
    assert report.summary["unique_symbol_count"] >= 0
    assert report.summary["top_mapping_confidence"] in {"unknown", "low", "medium", "high"}


def test_v134wa_program_symbol_watchlist_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WAAShareInternalHotNewsProgramSymbolWatchlistPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_symbol_watchlist_packet"] == "read_ready_internal_only"
    assert rows["unique_symbols"] == "materialized"
