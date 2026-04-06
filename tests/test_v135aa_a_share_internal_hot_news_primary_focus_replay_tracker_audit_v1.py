from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aa_a_share_internal_hot_news_primary_focus_replay_tracker_audit_v1 import (
    V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer,
)


def test_v135aa_primary_focus_replay_tracker_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer(repo_root).analyze()

    assert report.summary["focus_match_row_count"] >= 1
    assert report.summary["focus_source_present_count"] >= 1
    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["current_primary_watch_symbol"]


def test_v135aa_primary_focus_replay_tracker_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AAAShareInternalHotNewsPrimaryFocusReplayTrackerAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["focus_match_row_count"] >= rows["focus_source_present_count"]
    assert rows["theme_match_count"] >= 1
    assert rows["symbol_match_count"] >= 1
