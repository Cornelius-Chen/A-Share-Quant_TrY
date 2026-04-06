from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zs_a_share_internal_hot_news_accepted_rotation_shadow_change_signal_audit_v1 import (
    V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer,
)


def test_v134zs_accepted_rotation_shadow_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}


def test_v134zs_accepted_rotation_shadow_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZSAShareInternalHotNewsAcceptedRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 3
