from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pm_a_share_replay_market_context_residual_classification_audit_v1 import (
    V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer,
)


def test_v134pm_market_context_residual_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["missing_residual_count"] == 3
    assert report.summary["pre_coverage_count"] == 2
    assert report.summary["off_calendar_count"] == 1


def test_v134pm_market_context_residual_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PMAShareReplayMarketContextResidualClassificationAuditV1Analyzer(repo_root).analyze()
    classes = {row["decision_trade_date"]: row["residual_class"] for row in report.rows}

    assert classes["2023-09-22"] == "pre_coverage_shadow_slice"
    assert classes["2023-12-08"] == "pre_coverage_shadow_slice"
    assert classes["2026-03-28"] == "off_calendar_shadow_slice"
