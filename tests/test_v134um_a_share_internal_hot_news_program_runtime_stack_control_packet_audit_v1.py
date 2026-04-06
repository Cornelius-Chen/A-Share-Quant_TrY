from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134um_a_share_internal_hot_news_program_runtime_stack_control_packet_audit_v1 import (
    V134UMAShareInternalHotNewsProgramRuntimeStackControlPacketAuditV1Analyzer,
)


def test_v134um_runtime_stack_control_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UMAShareInternalHotNewsProgramRuntimeStackControlPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["supervisor_mode"] in {"steady_supervision", "tight_supervision", "elevated_supervision", "interrupt_supervision"}
    assert report.summary["supervision_loop_mode"] in {
        "steady_supervision_loop",
        "tight_supervision_loop",
        "interrupt_supervision_loop",
    }
    assert report.summary["signal_priority"] in {"p1", "p2"}


def test_v134um_runtime_stack_control_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UMAShareInternalHotNewsProgramRuntimeStackControlPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_control_packet"] == "read_ready_internal_only"
    assert rows["supervisor_mode"] == "materialized"
    assert rows["supervision_loop_mode"] == "materialized"
    assert rows["contract_action"] == "materialized"
    assert rows["signal_priority"] == "materialized"
