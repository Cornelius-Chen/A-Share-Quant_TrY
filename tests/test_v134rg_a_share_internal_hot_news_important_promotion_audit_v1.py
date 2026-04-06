from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rg_a_share_internal_hot_news_important_promotion_audit_v1 import (
    V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer,
)


def test_v134rg_important_promotion_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["important_promotion_row_count"] >= 0
    assert report.summary["important_queue_row_count"] >= 0
    assert report.summary["tier_1_count"] >= 0


def test_v134rg_important_promotion_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["important_promotion_registry"] == "materialized"
    assert rows["important_trading_queue"] == "read_ready_internal_only"
