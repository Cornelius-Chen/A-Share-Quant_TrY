from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qh_a_share_qg_runtime_promotion_direction_triage_v1 import (
    V134QHAShareQGRuntimePromotionDirectionTriageV1Analyzer,
)


def test_v134qh_runtime_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QHAShareQGRuntimePromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["priority_runtime_candidate_count"] == 1
    assert report.summary["excluded_runtime_row_count"] == 2


def test_v134qh_runtime_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QHAShareQGRuntimePromotionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "only_first_runtime_promotion_candidate" in rows["network_html_article_fetch"]
    assert "review_only_excluded_adapter" in rows["network_social_column_fetch"]
