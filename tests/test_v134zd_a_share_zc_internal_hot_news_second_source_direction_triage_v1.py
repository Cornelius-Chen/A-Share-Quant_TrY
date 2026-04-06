from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zd_a_share_zc_internal_hot_news_second_source_direction_triage_v1 import (
    V134ZDAShareZCInternalHotNewsSecondSourceDirectionTriageV1Analyzer,
)


def test_v134zd_second_source_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZDAShareZCInternalHotNewsSecondSourceDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["primary_theme_hit_count"] >= 0
    assert report.summary["probe_theme_hit_count"] >= 0


def test_v134zd_second_source_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZDAShareZCInternalHotNewsSecondSourceDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
