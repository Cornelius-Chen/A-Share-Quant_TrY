from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ad_a_share_ac_internal_hot_news_challenger_focus_direction_triage_v1 import (
    V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Analyzer,
)


def test_v135ad_challenger_focus_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["challenger_row_count"] >= 1
    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["top_challenger_theme_slug"] not in {"", "none", report.summary["current_primary_theme_slug"]}


def test_v135ad_challenger_focus_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ADAShareACInternalHotNewsChallengerFocusDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
