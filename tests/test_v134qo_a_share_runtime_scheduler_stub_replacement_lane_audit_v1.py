from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qo_a_share_runtime_scheduler_stub_replacement_lane_audit_v1 import (
    V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer,
)


def test_v134qo_runtime_stub_lane_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer(repo_root).analyze()

    assert report.summary["lane_row_count"] == 1
    assert report.summary["excluded_row_count"] == 2


def test_v134qo_runtime_stub_lane_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QOAShareRuntimeSchedulerStubReplacementLaneAuditV1Analyzer(repo_root).analyze()

    row = report.lane_rows[0]
    assert row["adapter_id"] == "network_html_article_fetch"
    assert row["lane_state"] == "scheduler_stub_replacement_lane_materialized"

