from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kp_a_share_feature_foundation_audit_v1 import (
    V134KPAShareFeatureFoundationAuditV1Analyzer,
)


def test_v134kp_feature_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KPAShareFeatureFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["feature_registry_count"] == 9
    assert report.summary["feature_surface_row_count"] == 566
    assert report.summary["representation_backlog_count"] == 1


def test_v134kp_feature_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KPAShareFeatureFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["feature_component"]: row for row in report.feature_rows}

    assert rows["feature_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["representation_backlog"]["component_state"] == "backlog_materialized_not_computed"
