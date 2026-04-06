from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zt_a_share_zs_internal_hot_news_accepted_rotation_shadow_change_direction_triage_v1 import (
    V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Analyzer,
)


def test_v134zt_accepted_rotation_shadow_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert "authoritative_status" in report.summary
    assert report.summary["signal_priority"] in {"p1", "p2"}


def test_v134zt_accepted_rotation_shadow_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZTAShareZSInternalHotNewsAcceptedRotationShadowChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
