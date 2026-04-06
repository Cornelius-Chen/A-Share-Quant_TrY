from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tw_a_share_internal_hot_news_program_orchestration_loop_signal_feed_audit_v1 import (
    V134TWAShareInternalHotNewsProgramOrchestrationLoopSignalFeedAuditV1Analyzer,
)


def test_v134tw_program_orchestration_loop_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TWAShareInternalHotNewsProgramOrchestrationLoopSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["orchestration_loop_signal_mode"] in {
        "interrupt_orchestration_loop",
        "tight_orchestration_loop",
        "steady_orchestration_loop",
    }
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["reopen_target"] in {"none", "orchestration_packet", "orchestration_packet_and_scheduler_layers"}


def test_v134tw_program_orchestration_loop_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TWAShareInternalHotNewsProgramOrchestrationLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["orchestration_loop_signal_feed"] == "read_ready_internal_only"
    assert rows["orchestration_loop_signal_mode"] == "materialized"
    assert rows["signal_priority"] == "materialized"
    assert rows["reopen_target"] == "materialized"
