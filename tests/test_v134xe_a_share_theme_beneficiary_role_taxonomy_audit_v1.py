from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134xe_a_share_theme_beneficiary_role_taxonomy_audit_v1 import (
    V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer,
)


def test_v134xe_theme_beneficiary_role_taxonomy_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer(repo_root).analyze()

    assert report.summary["role_variant_count"] >= 3
    assert report.summary["normalized_role_family_count"] >= 2
    assert report.summary["linkage_class_count"] >= 2


def test_v134xe_theme_beneficiary_role_taxonomy_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134XEAShareThemeBeneficiaryRoleTaxonomyAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "role_variant_count" in rows
    assert "normalized_role_family_count" in rows
