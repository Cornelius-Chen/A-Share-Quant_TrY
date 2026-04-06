from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sn_a_share_sm_internal_hot_news_program_change_action_signal_direction_triage_v1 import (
    V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Analyzer,
)


def test_v134sn_program_change_action_signal_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "action-level_change_signal" in report.summary["authoritative_status"]


def test_v134sn_program_change_action_signal_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SNAShareSMInternalHotNewsProgramChangeActionSignalDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
