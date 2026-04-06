from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zr_a_share_zq_internal_hot_news_accepted_rotation_shadow_control_direction_triage_v1 import (
    V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Analyzer,
)


def test_v134zr_accepted_rotation_shadow_control_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Analyzer(repo_root).analyze()

    assert "authoritative_status" in report.summary
    assert report.summary["shadow_top_watch_symbol"]


def test_v134zr_accepted_rotation_shadow_control_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZRAShareZQInternalHotNewsAcceptedRotationShadowControlDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
