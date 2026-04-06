from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zj_a_share_zi_internal_hot_news_controlled_merge_candidate_consumer_direction_triage_v1 import (
    V134ZJAShareZIInternalHotNewsControlledMergeCandidateConsumerDirectionTriageV1Analyzer,
)


def test_v134zj_candidate_consumer_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZJAShareZIInternalHotNewsControlledMergeCandidateConsumerDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["preview_row_count"] > 0
    assert report.summary["consumer_stability_state"]


def test_v134zj_candidate_consumer_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZJAShareZIInternalHotNewsControlledMergeCandidateConsumerDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
