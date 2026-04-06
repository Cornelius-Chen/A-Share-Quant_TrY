from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sr_a_share_sq_internal_hot_news_program_status_change_direction_triage_v1 import (
    V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Analyzer,
)


def test_v134sr_program_status_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "status-level_change_signal" in report.summary["authoritative_status"]


def test_v134sr_program_status_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 6
