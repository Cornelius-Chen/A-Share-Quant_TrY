from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ao_a_share_internal_hot_news_focus_competition_leaderboard_audit_v1 import (
    V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer,
)


def test_v135ao_focus_competition_leaderboard_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer(repo_root).analyze()

    assert report.summary["leaderboard_row_count"] >= 2
    assert report.summary["current_primary_theme_slug"] not in {"", "none"}
    assert report.summary["leader_theme_slug"] not in {"", "none"}
    assert report.summary["incumbent_is_leader"] in {"true", "false"}
    assert report.summary["current_primary_rank"] >= 1


def test_v135ao_focus_competition_leaderboard_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AOAShareInternalHotNewsFocusCompetitionLeaderboardAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert int(rows["leaderboard_row_count"]) >= 2
    assert rows["incumbent_is_leader"] in {"true", "false"}
