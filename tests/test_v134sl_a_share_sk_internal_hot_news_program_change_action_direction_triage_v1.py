from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sl_a_share_sk_internal_hot_news_program_change_action_direction_triage_v1 import (
    V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Analyzer,
)


def test_v134sl_program_change_action_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["action_row_count"] == 1
    assert "program_change_actions" in report.summary["authoritative_status"]


def test_v134sl_program_change_action_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
