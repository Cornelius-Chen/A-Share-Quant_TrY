from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tn_a_share_tm_internal_hot_news_program_scheduler_direction_triage_v1 import (
    V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Analyzer,
)


def test_v134tn_program_scheduler_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert "scheduler-packet" in report.summary["authoritative_status"]


def test_v134tn_program_scheduler_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
