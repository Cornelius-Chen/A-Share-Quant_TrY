from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sf_a_share_se_internal_hot_news_program_split_direction_triage_v1 import (
    V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Analyzer,
)


def test_v134sf_program_split_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["risk_feed_row_count"] >= 0
    assert report.summary["opportunity_feed_row_count"] >= 0
    assert "split_risk_and_opportunity_feeds" in report.summary["authoritative_status"]
    assert report.summary["risk_consumer_gate"]
    assert report.summary["opportunity_consumer_gate"]


def test_v134sf_program_split_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SFAShareSEInternalHotNewsProgramSplitDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
