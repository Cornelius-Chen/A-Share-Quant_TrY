from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sp_a_share_so_internal_hot_news_program_status_direction_triage_v1 import (
    V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Analyzer,
)


def test_v134sp_program_status_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["status_row_count"] == 1
    assert "outermost_consumer_entry" in report.summary["authoritative_status"]


def test_v134sp_program_status_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 8
