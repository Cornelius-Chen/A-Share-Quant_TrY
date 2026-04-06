from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134wd_a_share_wc_internal_hot_news_program_symbol_watch_summary_direction_triage_v1 import (
    V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Analyzer,
)


def test_v134wd_program_symbol_watch_summary_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["summary_row_count"] == 1
    assert report.summary["watchlist_row_count"] >= 0
    assert report.summary["top_watch_mapping_confidence"] in {"unknown", "low", "medium", "high"}


def test_v134wd_program_symbol_watch_summary_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WDAShareWCInternalHotNewsProgramSymbolWatchSummaryDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
