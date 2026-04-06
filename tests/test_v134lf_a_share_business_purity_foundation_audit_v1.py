from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lf_a_share_business_purity_foundation_audit_v1 import (
    V134LFAShareBusinessPurityFoundationAuditV1Analyzer,
)


def test_v134lf_business_purity_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LFAShareBusinessPurityFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["business_reference_count"] == 82
    assert report.summary["concept_purity_count"] == 82
    assert report.summary["sector_backed_with_concepts_count"] > 0
    assert report.summary["residual_count"] >= 0


def test_v134lf_business_purity_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LFAShareBusinessPurityFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["business_reference"]["component_state"] == "materialized_bootstrap"
    assert rows["residual_backlog"]["component_state"] == "materialized_named_residuals"
