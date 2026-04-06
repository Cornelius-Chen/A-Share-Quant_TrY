from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nf_a_share_ne_index_daily_source_gap_direction_triage_v1 import (
    V134NFAShareNEIndexDailySourceGapDirectionTriageV1Analyzer,
)


def test_v134nf_index_daily_source_gap_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NFAShareNEIndexDailySourceGapDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "index_daily_true_source_gap_closed_reaudit_required"


def test_v134nf_index_daily_source_gap_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NFAShareNEIndexDailySourceGapDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}
    assert rows["index_daily_source_horizon"]["direction"].startswith("retire_old_true_source_gap")
