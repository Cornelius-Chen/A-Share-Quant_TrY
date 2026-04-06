from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ca_a_share_internal_hot_news_runtime_scheduler_audit_v1 import (
    V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Analyzer,
)


def test_v135ca_runtime_scheduler_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Analyzer(repo_root).analyze()

    assert report.summary["runtime_state"] == "cycle_completed"
    assert report.summary["executed_step_count"] >= 20
    assert report.summary["cls_fetch_row_count"] > 0
    assert report.summary["sina_fetch_row_count"] > 0
    assert report.summary["top_opportunity_theme"] not in {"", "none"}
    assert report.summary["top_watch_symbol"]
    assert report.summary["retention_active_queue_count"] >= 0
    assert report.summary["retention_expired_cleanup_count"] >= 0
    assert report.summary["retention_cap_pruned_file_count"] >= 0
    assert report.summary["retention_cap_removed_row_count"] >= 0


def test_v135ca_runtime_scheduler_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["runtime_state"] == "cycle_completed"
    assert int(rows["executed_step_count"]) >= 20
    assert int(rows["cls_fetch_row_count"]) > 0
    assert int(rows["sina_fetch_row_count"]) > 0
    assert int(rows["retention_active_queue_count"]) >= 0
    assert int(rows["retention_cap_pruned_file_count"]) >= 0
    assert int(rows["retention_cap_removed_row_count"]) >= 0
