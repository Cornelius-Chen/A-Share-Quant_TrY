from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134vh_a_share_vg_theme_overlap_governance_direction_triage_v1 import (
    V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Analyzer,
)


def test_v134vh_theme_overlap_governance_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["governance_rule_count"] >= 7
    assert report.summary["resolved_overlap_count"] >= 7
    assert report.summary["unresolved_overlap_count"] == 0


def test_v134vh_theme_overlap_governance_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 2
