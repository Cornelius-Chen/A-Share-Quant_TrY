from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ak_a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_audit_v1 import (
    V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer,
)


def test_v135ak_challenger_primary_consumer_promotion_plan_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()

    assert report.summary["rotation_review_state"] in {
        "hold_incumbent_focus",
        "keep_incumbent_but_raise_review_attention",
        "open_next_rotation_review",
    }
    assert report.summary["shadow_change_signal_priority"] == "p1"
    assert report.summary["challenger_top_opportunity_theme"] not in {"", "none"}
    assert report.summary["challenger_top_watch_symbol"]
    assert report.summary["plan_step_count"] >= 4


def test_v135ak_challenger_primary_consumer_promotion_plan_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 5
