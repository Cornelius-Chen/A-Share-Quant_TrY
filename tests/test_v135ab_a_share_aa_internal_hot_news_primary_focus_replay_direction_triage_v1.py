from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ab_a_share_aa_internal_hot_news_primary_focus_replay_direction_triage_v1 import (
    V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Analyzer,
)


def test_v135ab_primary_focus_replay_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["focus_source_present_count"] >= 1
    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["current_primary_watch_symbol"]


def test_v135ab_primary_focus_replay_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ABAShareAAInternalHotNewsPrimaryFocusReplayDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
