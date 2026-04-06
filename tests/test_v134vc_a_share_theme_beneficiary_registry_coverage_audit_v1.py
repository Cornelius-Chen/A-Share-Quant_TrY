from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134vc_a_share_theme_beneficiary_registry_coverage_audit_v1 import (
    V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer,
)


def test_v134vc_theme_beneficiary_registry_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer(repo_root).analyze()

    assert report.summary["theme_count"] >= 10
    assert report.summary["registry_row_count"] >= report.summary["theme_count"]
    assert report.summary["registry_alias_intersection_count"] >= 10


def test_v134vc_theme_beneficiary_registry_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VCAShareThemeBeneficiaryRegistryCoverageAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "theme_count" in rows
    assert "registry_row_count" in rows
