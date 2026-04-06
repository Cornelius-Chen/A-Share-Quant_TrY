from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135av_a_share_au_internal_hot_news_focus_rotation_readiness_direction_triage_v1 import (
    V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Analyzer,
)


def test_v135av_focus_rotation_readiness_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert report.summary["rotation_readiness_priority"] in {"p1", "p2", "p3"}
    assert report.summary["rotation_readiness_state"] not in {"", "none"}


def test_v135av_focus_rotation_readiness_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AVAShareAUInternalHotNewsFocusRotationReadinessDirectionTriageV1Analyzer(
        repo_root
    ).analyze()

    assert len(report.triage_rows) == 3
