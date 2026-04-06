from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zc_a_share_internal_hot_news_second_source_probe_comparison_audit_v1 import (
    V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Analyzer,
)


def test_v134zc_second_source_probe_comparison_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Analyzer(repo_root).analyze()

    assert report.summary["primary_sample_row_count"] > 0
    assert report.summary["probe_sample_row_count"] > 0


def test_v134zc_second_source_probe_comparison_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "primary_theme_hit_count" in rows
    assert "probe_theme_hit_count" in rows
