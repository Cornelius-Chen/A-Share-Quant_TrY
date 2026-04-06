from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ba_a_share_internal_hot_news_focus_scoring_surface_audit_v1 import (
    V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Analyzer,
)


def test_v135ba_focus_scoring_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["scored_row_count"] >= 2
    assert report.summary["top_theme_slug"] not in {"", "none"}
    assert report.summary["top_watch_symbol"]
    assert report.summary["top_focus_total_score"] > 0


def test_v135ba_focus_scoring_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135BAAShareInternalHotNewsFocusScoringSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert int(rows["scored_row_count"]) >= 2
    assert rows["top_theme_slug"] not in {"", "none"}
