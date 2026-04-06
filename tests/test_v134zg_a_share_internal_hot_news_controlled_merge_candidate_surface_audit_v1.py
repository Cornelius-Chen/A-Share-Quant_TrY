from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zg_a_share_internal_hot_news_controlled_merge_candidate_surface_audit_v1 import (
    V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer,
)


def test_v134zg_controlled_merge_candidate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_row_count"] > 0
    assert report.summary["sina_additive_count"] > 0


def test_v134zg_controlled_merge_candidate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["candidate_row_count"] == rows["cls_primary_count"] + rows["sina_additive_count"]
    assert rows["unique_theme_count"] > 0
