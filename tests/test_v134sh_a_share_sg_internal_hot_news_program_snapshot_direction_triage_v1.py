from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sh_a_share_sg_internal_hot_news_program_snapshot_direction_triage_v1 import (
    V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Analyzer,
)


def test_v134sh_program_snapshot_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["snapshot_row_count"] == 1
    assert "single_program_snapshot_row" in report.summary["authoritative_status"]
    assert report.summary["snapshot_consumer_gate_mode"]


def test_v134sh_program_snapshot_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
