from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sd_a_share_sc_internal_hot_news_minimal_view_direction_triage_v1 import (
    V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Analyzer,
)


def test_v134sd_minimal_view_direction_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["minimal_view_row_count"] > 0
    assert "compact_trading_program_minimal_view" in report.summary["authoritative_status"]


def test_v134sd_minimal_view_direction_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SDAShareSCInternalHotNewsMinimalViewDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
