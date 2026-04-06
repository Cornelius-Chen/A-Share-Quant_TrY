from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uz_a_share_uy_internal_hot_news_program_runtime_stack_control_loop_execution_direction_triage_v1 import (
    V134UZAShareUYInternalHotNewsProgramRuntimeStackControlLoopExecutionDirectionTriageV1Analyzer,
)


def test_v134uz_runtime_stack_control_loop_execution_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UZAShareUYInternalHotNewsProgramRuntimeStackControlLoopExecutionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["contract_row_count"] == 1
    assert "runtime-stack_control-loop_execution_contract" in report.summary["authoritative_status"]


def test_v134uz_runtime_stack_control_loop_execution_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UZAShareUYInternalHotNewsProgramRuntimeStackControlLoopExecutionDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
