from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ap_a_share_ao_internal_hot_news_focus_competition_direction_triage_v1 import (
    V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Analyzer,
)


def test_v135ap_focus_competition_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["leader_theme_slug"] not in {"", "none"}
    assert report.summary["incumbent_is_leader"] in {"true", "false"}


def test_v135ap_focus_competition_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135APAShareAOInternalHotNewsFocusCompetitionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
