from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ve_a_share_theme_alias_hit_drill_audit_v1 import (
    V134VEAShareThemeAliasHitDrillAuditV1Analyzer,
)


def test_v134ve_theme_alias_hit_drill_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VEAShareThemeAliasHitDrillAuditV1Analyzer(repo_root).analyze()

    assert report.summary["case_count"] >= 20
    assert report.summary["expected_covered_count"] == report.summary["case_count"]
    assert report.summary["partial_or_miss_count"] == 0


def test_v134ve_theme_alias_hit_drill_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VEAShareThemeAliasHitDrillAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert "case_count" in rows
    assert "exact_expected_hit_count" in rows
