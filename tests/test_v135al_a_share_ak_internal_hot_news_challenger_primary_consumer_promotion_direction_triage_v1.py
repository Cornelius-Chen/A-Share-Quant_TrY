from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135al_a_share_ak_internal_hot_news_challenger_primary_consumer_promotion_direction_triage_v1 import (
    V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Analyzer,
)


def test_v135al_challenger_primary_consumer_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["rotation_review_state"] in {
        "hold_incumbent_focus",
        "keep_incumbent_but_raise_review_attention",
        "open_next_rotation_review",
    }
    assert report.summary["challenger_top_opportunity_theme"] not in {"", "none"}
    assert report.summary["challenger_top_watch_symbol"]


def test_v135al_challenger_primary_consumer_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
