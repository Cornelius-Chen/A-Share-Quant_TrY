from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134wf_a_share_we_internal_hot_news_program_symbol_watch_summary_change_direction_triage_v1 import (
    V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Analyzer,
)


def test_v134wf_program_symbol_watch_summary_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["change_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}


def test_v134wf_program_symbol_watch_summary_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WFAShareWEInternalHotNewsProgramSymbolWatchSummaryChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
