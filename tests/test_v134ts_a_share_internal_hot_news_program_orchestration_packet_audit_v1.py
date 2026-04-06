from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ts_a_share_internal_hot_news_program_orchestration_packet_audit_v1 import (
    V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer,
)


def test_v134ts_program_orchestration_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["orchestration_mode"] in {
        "interrupt_orchestration",
        "tight_orchestration",
        "steady_orchestration",
    }
    assert report.summary["scheduler_loop_signal_mode"] in {
        "interrupt_requeue",
        "tight_poll_requeue",
        "steady_polling",
    }


def test_v134ts_program_orchestration_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["orchestration_packet"] == "read_ready_internal_only"
    assert rows["orchestration_mode"] == "materialized"
    assert rows["scheduler_loop_signal_mode"] == "materialized"
    assert rows["runtime_consumer_mode"] == "materialized"
