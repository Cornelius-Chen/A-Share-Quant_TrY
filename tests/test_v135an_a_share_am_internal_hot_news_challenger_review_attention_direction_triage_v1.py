from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135an_a_share_am_internal_hot_news_challenger_review_attention_direction_triage_v1 import (
    V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Analyzer,
)


def test_v135an_challenger_review_attention_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert report.summary["incumbent_theme_slug"] not in {"", "none"}
    assert report.summary["challenger_theme_slug"] not in {"", "none", report.summary["incumbent_theme_slug"]}
    assert report.summary["attention_priority"] in {"p1", "p2", "p3"}


def test_v135an_challenger_review_attention_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ANAShareAMInternalHotNewsChallengerReviewAttentionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert len(report.triage_rows) == 3
