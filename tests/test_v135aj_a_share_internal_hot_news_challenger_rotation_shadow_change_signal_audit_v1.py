from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aj_a_share_internal_hot_news_challenger_rotation_shadow_change_signal_audit_v1 import (
    V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Analyzer,
)


def test_v135aj_challenger_rotation_shadow_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["top_opportunity_theme_change"] == "would_change"
    assert report.summary["top_watch_symbol_change"] == "would_change"
    assert report.summary["signal_priority"] == "p1"


def test_v135aj_challenger_rotation_shadow_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AJAShareInternalHotNewsChallengerRotationShadowChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 3
