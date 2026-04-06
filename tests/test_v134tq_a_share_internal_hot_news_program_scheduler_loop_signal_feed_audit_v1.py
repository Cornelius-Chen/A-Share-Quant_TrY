from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tq_a_share_internal_hot_news_program_scheduler_loop_signal_feed_audit_v1 import (
    V134TQAShareInternalHotNewsProgramSchedulerLoopSignalFeedAuditV1Analyzer,
)


def test_v134tq_program_scheduler_loop_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TQAShareInternalHotNewsProgramSchedulerLoopSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["scheduler_loop_signal_mode"] in {
        "interrupt_requeue",
        "tight_poll_requeue",
        "steady_polling",
    }
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["reschedule_target"] in {"none", "scheduler_queue", "scheduler_queue_and_runtime_loop"}


def test_v134tq_program_scheduler_loop_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TQAShareInternalHotNewsProgramSchedulerLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["scheduler_loop_signal_feed"] == "read_ready_internal_only"
    assert rows["scheduler_loop_signal_mode"] == "materialized"
    assert rows["signal_priority"] == "materialized"
    assert rows["reschedule_target"] == "materialized"
