from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tm_a_share_internal_hot_news_program_scheduler_packet_audit_v1 import (
    V134TMAShareInternalHotNewsProgramSchedulerPacketAuditV1Analyzer,
)


def test_v134tm_program_scheduler_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TMAShareInternalHotNewsProgramSchedulerPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["scheduler_mode"] in {"steady_schedule", "tight_requeue", "interrupt_and_requeue"}
    assert report.summary["contract_action"] in {
        "interrupt_loop_and_reopen_target",
        "elevate_and_reopen_target",
        "elevate_polling_only",
        "reopen_target_without_interrupt",
        "keep_passive_polling",
    }


def test_v134tm_program_scheduler_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TMAShareInternalHotNewsProgramSchedulerPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["scheduler_packet"] == "read_ready_internal_only"
    assert rows["scheduler_mode"] == "materialized"
    assert rows["contract_action"] == "materialized"
    assert rows["sleep_strategy"] == "materialized"
