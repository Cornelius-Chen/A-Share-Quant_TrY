from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134re_a_share_internal_hot_news_event_cluster_audit_v1 import (
    V134REAShareInternalHotNewsEventClusterAuditV1Analyzer,
)


def test_v134re_event_cluster_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134REAShareInternalHotNewsEventClusterAuditV1Analyzer(repo_root).analyze()

    assert report.summary["cluster_row_count"] > 0
    assert report.summary["deduped_row_count"] > 0
    assert report.summary["duplicate_reduction_count"] >= 0


def test_v134re_event_cluster_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134REAShareInternalHotNewsEventClusterAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["event_cluster_surface"] == "materialized"
    assert rows["deduped_event_stream"] == "read_ready_internal_only"
