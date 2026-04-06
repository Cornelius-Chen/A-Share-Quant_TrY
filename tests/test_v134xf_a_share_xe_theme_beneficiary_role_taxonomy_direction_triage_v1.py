from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134xf_a_share_xe_theme_beneficiary_role_taxonomy_direction_triage_v1 import (
    V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Analyzer,
)


def test_v134xf_theme_beneficiary_role_taxonomy_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["role_variant_count"] >= 3
    assert report.summary["linkage_class_count"] >= 2


def test_v134xf_theme_beneficiary_role_taxonomy_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134XFAShareXEThemeBeneficiaryRoleTaxonomyDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
