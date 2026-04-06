from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kx_a_share_serving_foundation_audit_v1 import (
    V134KXAShareServingFoundationAuditV1Analyzer,
)


def test_v134kx_serving_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KXAShareServingFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["research_view_count"] == 6
    assert report.summary["shadow_view_count"] == 4
    assert report.summary["live_like_view_count"] == 2
    assert report.summary["active_serving_route_count"] == 2


def test_v134kx_serving_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KXAShareServingFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["serving_component"]: row for row in report.serving_rows}

    assert rows["shadow_views"]["component_state"] == "materialized_bootstrap_read_only"
    assert rows["live_like_views"]["component_state"] == "deferred_backlog"
