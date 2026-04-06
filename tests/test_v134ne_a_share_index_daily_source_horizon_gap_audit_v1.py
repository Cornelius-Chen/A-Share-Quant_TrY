from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ne_a_share_index_daily_source_horizon_gap_audit_v1 import (
    V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer,
)


def test_v134ne_index_daily_source_gap_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["raw_file_count"] == 10
    assert report.summary["beyond_2024_source_count"] == 0
    assert report.summary["max_raw_coverage_end"] == "2024-12-31"


def test_v134ne_index_daily_source_gap_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NEAShareIndexDailySourceHorizonGapAuditV1Analyzer(repo_root).analyze()
    assert all(row["extends_beyond_2024"] is False for row in report.rows)
