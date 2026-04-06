from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ac_a_share_internal_hot_news_challenger_focus_comparison_audit_v1 import (
    V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer,
)


def test_v135ac_challenger_focus_comparison_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer(repo_root).analyze()

    assert report.summary["challenger_row_count"] >= 1
    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["current_primary_watch_symbol"]
    assert report.summary["top_challenger_theme_slug"] not in {"", "none", report.summary["current_primary_theme_slug"]}


def test_v135ac_challenger_focus_comparison_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert int(rows["challenger_row_count"]) >= 1
    assert rows["top_challenger_symbol"] != report.summary["current_primary_watch_symbol"]
