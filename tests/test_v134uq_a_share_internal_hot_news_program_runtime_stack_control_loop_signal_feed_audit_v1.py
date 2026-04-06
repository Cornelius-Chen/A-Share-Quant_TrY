from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uq_a_share_internal_hot_news_program_runtime_stack_control_loop_signal_feed_audit_v1 import (
    V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer,
)


def test_v134uq_runtime_stack_control_loop_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["runtime_stack_control_loop_signal_mode"] in {
        "steady_runtime_stack_control_loop",
        "tight_runtime_stack_control_loop",
        "interrupt_runtime_stack_control_loop",
    }
    assert report.summary["reopen_target"] in {
        "none",
        "runtime_stack_control_packet",
        "runtime_stack_supervisor_surface",
        "runtime_stack_control_packet_and_supervision_layers",
    }


def test_v134uq_runtime_stack_control_loop_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_control_loop_signal_feed"] == "read_ready_internal_only"
    assert rows["runtime_stack_control_loop_signal_mode"] == "materialized"
    assert rows["signal_priority"] == "materialized"
    assert rows["reopen_target"] == "materialized"
