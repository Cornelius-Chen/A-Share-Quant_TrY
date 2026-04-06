from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zv_a_share_zu_internal_hot_news_accepted_rotation_primary_consumer_promotion_direction_triage_v1 import (
    V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Analyzer,
)


def test_v134zv_primary_consumer_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert "authoritative_status" in report.summary
    assert report.summary["plan_step_count"] >= 4


def test_v134zv_primary_consumer_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
