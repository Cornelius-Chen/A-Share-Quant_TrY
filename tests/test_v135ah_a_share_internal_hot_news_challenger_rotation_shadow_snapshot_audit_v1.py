from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ah_a_share_internal_hot_news_challenger_rotation_shadow_snapshot_audit_v1 import (
    V135AHAShareInternalHotNewsChallengerRotationShadowSnapshotAuditV1Analyzer,
)


def test_v135ah_challenger_rotation_shadow_snapshot_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AHAShareInternalHotNewsChallengerRotationShadowSnapshotAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_top_opportunity_theme"] not in {"", "none"}
    assert report.summary["shadow_top_opportunity_theme"] not in {"", "none", report.summary["current_top_opportunity_theme"]}
    assert report.summary["current_top_watch_symbol"]
    assert report.summary["shadow_top_watch_symbol"] != report.summary["current_top_watch_symbol"]


def test_v135ah_challenger_rotation_shadow_snapshot_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AHAShareInternalHotNewsChallengerRotationShadowSnapshotAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 4
