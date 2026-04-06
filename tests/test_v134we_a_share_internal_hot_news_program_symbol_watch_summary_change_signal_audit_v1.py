from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134we_a_share_internal_hot_news_program_symbol_watch_summary_change_signal_audit_v1 import (
    V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer,
)


def test_v134we_program_symbol_watch_summary_change_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["change_row_count"] == 1
    assert report.summary["top_watch_symbol_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["top_watch_bundle_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["top_watch_theme_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["signal_priority"] in {"p1", "p2"}


def test_v134we_program_symbol_watch_summary_change_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134WEAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["symbol_watch_summary_change_signal"] == "read_ready_internal_only"
    assert rows["top_watch_symbol_change"] == "materialized"
    assert rows["signal_priority"] == "materialized"
