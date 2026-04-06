from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zu_a_share_internal_hot_news_accepted_rotation_primary_consumer_promotion_plan_audit_v1 import (
    V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer,
)


def test_v134zu_primary_consumer_promotion_plan_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()

    assert report.summary["plan_state"]
    assert report.summary["plan_step_count"] >= 4


def test_v134zu_primary_consumer_promotion_plan_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 5
