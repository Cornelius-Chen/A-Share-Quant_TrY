from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134vf_a_share_ve_theme_alias_hit_direction_triage_v1 import (
    V134VFAShareVEThemeAliasHitDirectionTriageV1Analyzer,
)


def test_v134vf_theme_alias_hit_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VFAShareVEThemeAliasHitDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["case_count"] >= 20
    assert report.summary["expected_covered_count"] == report.summary["case_count"]
    assert report.summary["partial_or_miss_count"] == 0


def test_v134vf_theme_alias_hit_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VFAShareVEThemeAliasHitDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
