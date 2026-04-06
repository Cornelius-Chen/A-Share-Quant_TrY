from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zh_a_share_zg_internal_hot_news_controlled_merge_candidate_direction_triage_v1 import (
    V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Analyzer,
)


def test_v134zh_controlled_merge_candidate_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_row_count"] > 0
    assert report.summary["sina_additive_count"] > 0


def test_v134zh_controlled_merge_candidate_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
