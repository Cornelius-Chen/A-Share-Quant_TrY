from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sj_a_share_si_internal_hot_news_program_snapshot_change_direction_triage_v1 import (
    V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Analyzer,
)


def test_v134sj_program_snapshot_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["change_row_count"] == 1
    assert "snapshot_change_signal" in report.summary["authoritative_status"]


def test_v134sj_program_snapshot_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SJAShareSIInternalHotNewsProgramSnapshotChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
