from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zl_a_share_zk_internal_hot_news_controlled_merge_candidate_promotion_direction_triage_v1 import (
    V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Analyzer,
)


def test_v134zl_candidate_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["promotion_gate_state"] in {"promotion_gate_hold", "promotion_gate_clear"}
    assert "authoritative_status" in report.summary


def test_v134zl_candidate_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
