from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134vd_a_share_vc_theme_beneficiary_registry_direction_triage_v1 import (
    V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Analyzer,
)


def test_v134vd_theme_beneficiary_registry_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["theme_count"] >= 10
    assert report.summary["registry_alias_intersection_count"] >= 10


def test_v134vd_theme_beneficiary_registry_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134VDAShareVCThemeBeneficiaryRegistryDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
