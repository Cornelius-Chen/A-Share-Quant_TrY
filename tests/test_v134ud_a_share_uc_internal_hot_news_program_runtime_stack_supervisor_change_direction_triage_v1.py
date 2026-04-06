from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ud_a_share_uc_internal_hot_news_program_runtime_stack_supervisor_change_direction_triage_v1 import (
    V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Analyzer,
)


def test_v134ud_runtime_stack_supervisor_change_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "runtime-stack_supervisor_change_signal" in report.summary["authoritative_status"]


def test_v134ud_runtime_stack_supervisor_change_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
