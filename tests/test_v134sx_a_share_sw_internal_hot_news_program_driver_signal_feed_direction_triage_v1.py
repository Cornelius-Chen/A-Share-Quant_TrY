from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sx_a_share_sw_internal_hot_news_program_driver_signal_feed_direction_triage_v1 import (
    V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Analyzer,
)


def test_v134sx_driver_signal_feed_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "driver-escalation_signal-feed" in report.summary["authoritative_status"]


def test_v134sx_driver_signal_feed_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
