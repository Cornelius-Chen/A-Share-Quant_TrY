from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lq_a_share_review_activation_audit_v1 import (
    V134LQAShareReviewActivationAuditV1Analyzer,
)


def test_v134lq_review_activation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LQAShareReviewActivationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["review_registry_count"] == 3
    assert report.summary["low_confidence_queue_count"] == 45
    assert report.summary["attention_soft_queue_count"] == 4


def test_v134lq_review_activation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LQAShareReviewActivationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["review_activation_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["contradiction_queue"]["component_state"] == "active_bootstrap_queue"
