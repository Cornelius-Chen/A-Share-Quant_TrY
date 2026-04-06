from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ue_a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_audit_v1 import (
    V134UEAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedAuditV1Analyzer,
)


def test_v134ue_runtime_stack_supervisor_loop_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UEAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["supervision_loop_mode"] in {
        "interrupt_supervision_loop",
        "tight_supervision_loop",
        "steady_supervision_loop",
    }
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["reopen_target"] in {"none", "supervisor_surface", "supervisor_surface_and_lower_stacks"}


def test_v134ue_runtime_stack_supervisor_loop_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UEAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_supervisor_loop_signal_feed"] == "read_ready_internal_only"
    assert rows["supervision_loop_mode"] == "materialized"
    assert rows["signal_priority"] == "materialized"
    assert rows["reopen_target"] == "materialized"
