from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ur_a_share_uq_internal_hot_news_program_runtime_stack_control_loop_direction_triage_v1 import (
    V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Analyzer,
)


def test_v134ur_runtime_stack_control_loop_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert "runtime-stack_control_loop_signal_feed" in report.summary["authoritative_status"]


def test_v134ur_runtime_stack_control_loop_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
