from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ra_a_share_internal_hot_news_fastlane_activation_audit_v1 import (
    V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer,
)


def test_v134ra_internal_hot_news_fastlane_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["fetch_row_count"] > 0
    assert report.summary["fastlane_row_count"] > 0
    assert report.summary["retention_queue_count"] == report.summary["fastlane_row_count"]
    assert report.summary["runtime_state"] == "internal_only_active"


def test_v134ra_internal_hot_news_fastlane_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["internal_hot_news_runtime"] == "internal_only_active"
    assert rows["fastlane_pipeline"] == "pipeline_ready_for_trading_program"
    assert rows["retention"] == "hot_5d_ttl_active"
