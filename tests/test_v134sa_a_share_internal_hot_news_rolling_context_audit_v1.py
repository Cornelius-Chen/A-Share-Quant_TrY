from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sa_a_share_internal_hot_news_rolling_context_audit_v1 import (
    V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer,
)


def test_v134sa_rolling_context_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer(repo_root).analyze()

    assert report.summary["context_row_count"] > 0
    assert report.summary["important_impact_row_count"] >= 0
    assert report.summary["active_impact_count"] >= 0
    assert report.summary["accelerating_context_count"] >= 0
    assert report.summary["cooling_context_count"] >= 0


def test_v134sa_rolling_context_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SAAShareInternalHotNewsRollingContextAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["rolling_context_surface"] == "materialized"
    assert rows["important_impact_window"] == "materialized"
    assert rows["context_velocity"] == "materialized"
    assert rows["context_cooling"] == "materialized"
