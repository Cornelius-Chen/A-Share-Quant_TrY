from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ar_a_share_aq_internal_hot_news_focus_governance_tension_direction_triage_v1 import (
    V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Analyzer,
)


def test_v135ar_focus_governance_tension_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["leader_theme_slug"] not in {"", "none"}
    assert report.summary["tension_priority"] in {"p1", "p2", "p3"}


def test_v135ar_focus_governance_tension_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert len(report.triage_rows) == 3
