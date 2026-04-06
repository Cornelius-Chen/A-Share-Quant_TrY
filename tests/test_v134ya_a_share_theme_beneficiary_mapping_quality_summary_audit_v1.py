from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ya_a_share_theme_beneficiary_mapping_quality_summary_audit_v1 import (
    V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer,
)


def test_v134ya_theme_beneficiary_mapping_quality_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer(repo_root).analyze()

    assert report.summary["theme_count"] >= 10
    assert report.summary["direct_row_count"] >= 1
    assert report.summary["proxy_row_count"] >= 1


def test_v134ya_theme_beneficiary_mapping_quality_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YAAShareThemeBeneficiaryMappingQualitySummaryAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "theme_count" in rows
    assert "direct_clean_theme_count" in rows
