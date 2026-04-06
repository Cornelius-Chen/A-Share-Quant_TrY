from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ke_a_share_taxonomy_foundation_audit_v1 import (
    V134KEAShareTaxonomyFoundationAuditV1Analyzer,
)


def test_v134ke_taxonomy_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KEAShareTaxonomyFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["identity_symbol_count"] == 82
    assert report.summary["concept_membership_row_count"] > 0
    assert report.summary["sector_membership_row_count"] > 0
    assert report.summary["concept_covered_symbol_count"] > 0
    assert report.summary["sector_covered_symbol_count"] > 0


def test_v134ke_taxonomy_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KEAShareTaxonomyFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["taxonomy_component"]: row for row in report.taxonomy_rows}

    assert rows["concept_membership"]["component_state"] == "materialized_partial_foundation"
    assert rows["sector_membership"]["component_state"] == "materialized_partial_foundation"
    assert rows["business_reference"]["component_state"] == "backlog_materialized_not_filled"
