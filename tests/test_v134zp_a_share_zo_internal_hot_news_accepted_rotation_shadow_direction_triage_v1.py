from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zp_a_share_zo_internal_hot_news_accepted_rotation_shadow_direction_triage_v1 import (
    V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Analyzer,
)


def test_v134zp_accepted_rotation_shadow_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Analyzer(repo_root).analyze()

    assert "authoritative_status" in report.summary
    assert report.summary["shadow_top_watch_symbol"]


def test_v134zp_accepted_rotation_shadow_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZPAShareZOInternalHotNewsAcceptedRotationShadowDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
