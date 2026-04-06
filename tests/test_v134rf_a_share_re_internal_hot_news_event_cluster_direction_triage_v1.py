from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rf_a_share_re_internal_hot_news_event_cluster_direction_triage_v1 import (
    V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Analyzer,
)


def test_v134rf_event_cluster_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["cluster_row_count"] > 0
    assert report.summary["deduped_row_count"] > 0


def test_v134rf_event_cluster_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "deduped_event_stream" in rows["deduped_delivery"]
    assert "duplicate_reduction" in rows["duplicate_control"]
