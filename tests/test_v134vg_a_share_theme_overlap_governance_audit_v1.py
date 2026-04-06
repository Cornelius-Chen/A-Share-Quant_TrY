from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134vg_a_share_theme_overlap_governance_audit_v1 import (
    V134VGAShareThemeOverlapGovernanceAuditV1Analyzer,
)


def test_v134vg_theme_overlap_governance_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VGAShareThemeOverlapGovernanceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["governance_rule_count"] >= 7
    assert report.summary["resolved_overlap_count"] >= 7
    assert report.summary["unresolved_overlap_count"] == 0


def test_v134vg_theme_overlap_governance_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VGAShareThemeOverlapGovernanceAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "governance_rule_count" in rows
    assert "resolved_overlap_count" in rows
