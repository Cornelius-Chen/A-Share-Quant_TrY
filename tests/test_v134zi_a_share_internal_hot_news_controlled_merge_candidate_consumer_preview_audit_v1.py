from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zi_a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_audit_v1 import (
    V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Analyzer,
)


def test_v134zi_candidate_consumer_preview_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["preview_row_count"] > 0
    assert report.summary["additive_preview_count"] > 0


def test_v134zi_candidate_consumer_preview_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Analyzer(repo_root).analyze()

    assert any(row["metric"] == "top_opportunity_change_if_promoted" for row in report.rows)
    assert any(row["metric"] == "top_watch_change_if_promoted" for row in report.rows)
