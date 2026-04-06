from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134wb_a_share_wa_internal_hot_news_program_symbol_watchlist_packet_direction_triage_v1 import (
    V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Analyzer,
)


def test_v134wb_program_symbol_watchlist_packet_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["watchlist_row_count"] >= 0
    assert report.summary["unique_symbol_count"] >= 0
    assert report.summary["top_mapping_confidence"] in {"unknown", "low", "medium", "high"}


def test_v134wb_program_symbol_watchlist_packet_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WBAShareWAInternalHotNewsProgramSymbolWatchlistPacketDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
