from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rk_a_share_internal_hot_news_trading_program_ingress_audit_v1 import (
    V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer,
)


def test_v134rk_trading_program_ingress_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer(repo_root).analyze()

    assert report.summary["ingress_row_count"] > 0
    assert report.summary["important_ingress_count"] >= 0
    assert report.summary["board_specific_ingress_count"] >= 0
    assert report.summary["active_hot_window_count"] >= 0
    assert report.summary["important_copy_retained_count"] >= 0
    assert report.summary["impact_window_attached_count"] >= 0
    assert report.summary["accelerating_ingress_count"] >= 0
    assert report.summary["late_impact_window_count"] >= 0
    assert report.summary["focus_scored_ingress_count"] >= 0
    assert report.summary["top_focus_theme_slug"] != ""


def test_v134rk_trading_program_ingress_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["trading_program_ingress"] == "read_ready_internal_only"
    assert rows["important_ingress"] == "materialized"
    assert rows["context_velocity"] == "materialized"
    assert rows["impact_decay"] == "materialized"
    assert rows["focus_scoring"] == "materialized"
