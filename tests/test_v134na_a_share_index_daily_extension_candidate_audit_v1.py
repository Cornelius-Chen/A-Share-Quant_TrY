from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134na_a_share_index_daily_extension_candidate_audit_v1 import (
    V134NAAShareIndexDailyExtensionCandidateAuditV1Analyzer,
)


def test_v134na_index_daily_extension_candidate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NAAShareIndexDailyExtensionCandidateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["shadow_slice_count"] == 17
    assert report.summary["candidate_cover_count"] == 0
    assert report.summary["raw_index_coverage_end"] == "2024-12-31"


def test_v134na_index_daily_extension_candidate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NAAShareIndexDailyExtensionCandidateAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}
    assert rows["index_daily_extension_candidate_surface"]["component_state"] == "materialized_candidate_cover_surface"
