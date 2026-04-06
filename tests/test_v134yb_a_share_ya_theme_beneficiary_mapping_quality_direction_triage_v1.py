from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134yb_a_share_ya_theme_beneficiary_mapping_quality_direction_triage_v1 import (
    V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Analyzer,
)


def test_v134yb_theme_beneficiary_mapping_quality_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["theme_count"] >= 10
    assert report.summary["proxy_heavy_theme_count"] >= 0


def test_v134yb_theme_beneficiary_mapping_quality_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YBAShareYAThemeBeneficiaryMappingQualityDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
