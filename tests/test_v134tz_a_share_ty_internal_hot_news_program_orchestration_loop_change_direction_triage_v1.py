from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tz_a_share_ty_internal_hot_news_program_orchestration_loop_change_direction_triage_v1 import (
    V134TZAShareTYInternalHotNewsProgramOrchestrationLoopChangeDirectionTriageV1Analyzer,
)


def test_v134tz_program_orchestration_loop_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TZAShareTYInternalHotNewsProgramOrchestrationLoopChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "orchestration-loop_signal_change" in report.summary["authoritative_status"]


def test_v134tz_program_orchestration_loop_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TZAShareTYInternalHotNewsProgramOrchestrationLoopChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
