from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kt_a_share_market_foundation_audit_v1 import (
    V134KTAShareMarketFoundationAuditV1Analyzer,
)


def test_v134kt_market_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KTAShareMarketFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["daily_symbol_count"] == 8
    assert report.summary["daily_identity_overlap_count"] == 8
    assert report.summary["index_symbol_count"] == 3
    assert report.summary["intraday_trade_date_count"] == 102


def test_v134kt_market_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KTAShareMarketFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["market_component"]: row for row in report.market_rows}

    assert rows["daily_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["board_state_backlog"]["component_state"] == "backlog_materialized_not_yet_derived"
