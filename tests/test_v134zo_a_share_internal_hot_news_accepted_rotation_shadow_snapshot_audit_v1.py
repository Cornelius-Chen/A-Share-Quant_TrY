from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zo_a_share_internal_hot_news_accepted_rotation_shadow_snapshot_audit_v1 import (
    V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer,
)


def test_v134zo_accepted_rotation_shadow_snapshot_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_top_opportunity_theme"]
    assert report.summary["shadow_top_opportunity_theme"]


def test_v134zo_accepted_rotation_shadow_snapshot_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZOAShareInternalHotNewsAcceptedRotationShadowSnapshotAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 4
