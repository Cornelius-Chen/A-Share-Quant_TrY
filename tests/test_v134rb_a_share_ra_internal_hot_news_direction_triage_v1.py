from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rb_a_share_ra_internal_hot_news_direction_triage_v1 import (
    V134RBAShareRAInternalHotNewsDirectionTriageV1Analyzer,
)


def test_v134rb_internal_hot_news_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RBAShareRAInternalHotNewsDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["fetch_row_count"] > 0
    assert report.summary["fastlane_row_count"] > 0


def test_v134rb_internal_hot_news_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RBAShareRAInternalHotNewsDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "single_internal_fastlane_source" in rows["source_choice"]
    assert "5_days" in rows["retention"]
