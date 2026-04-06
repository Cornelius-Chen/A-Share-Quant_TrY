from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rh_a_share_rg_internal_hot_news_important_direction_triage_v1 import (
    V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Analyzer,
)


def test_v134rh_important_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["important_promotion_row_count"] >= 0
    assert report.summary["important_queue_row_count"] >= 0


def test_v134rh_important_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "deduped_guidance" in rows["promotion_logic"]
    assert "important_queue" in rows["trading_delivery"]
