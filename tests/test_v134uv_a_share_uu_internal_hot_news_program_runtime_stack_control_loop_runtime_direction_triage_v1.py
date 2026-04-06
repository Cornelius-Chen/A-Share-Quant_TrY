from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uv_a_share_uu_internal_hot_news_program_runtime_stack_control_loop_runtime_direction_triage_v1 import (
    V134UVAShareUUInternalHotNewsProgramRuntimeStackControlLoopRuntimeDirectionTriageV1Analyzer,
)


def test_v134uv_runtime_stack_control_loop_runtime_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UVAShareUUInternalHotNewsProgramRuntimeStackControlLoopRuntimeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["envelope_row_count"] == 1
    assert "runtime-stack_control-loop_runtime-envelope" in report.summary["authoritative_status"]


def test_v134uv_runtime_stack_control_loop_runtime_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UVAShareUUInternalHotNewsProgramRuntimeStackControlLoopRuntimeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
