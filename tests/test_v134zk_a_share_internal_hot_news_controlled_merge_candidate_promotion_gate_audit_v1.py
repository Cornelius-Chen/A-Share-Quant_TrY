from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zk_a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_audit_v1 import (
    V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer,
)


def test_v134zk_candidate_promotion_gate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["preview_row_count"] > 0
    assert report.summary["promotion_gate_state"] in {"promotion_gate_hold", "promotion_gate_clear"}


def test_v134zk_candidate_promotion_gate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer(repo_root).analyze()

    assert any(row["metric"] == "promotable_now" for row in report.rows)
