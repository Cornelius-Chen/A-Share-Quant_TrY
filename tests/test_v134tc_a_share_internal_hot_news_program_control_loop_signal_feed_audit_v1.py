from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tc_a_share_internal_hot_news_program_control_loop_signal_feed_audit_v1 import (
    V134TCAShareInternalHotNewsProgramControlLoopSignalFeedAuditV1Analyzer,
)


def test_v134tc_program_control_loop_signal_feed_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TCAShareInternalHotNewsProgramControlLoopSignalFeedAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["loop_signal_mode"] in {"interrupt", "elevate_attention", "passive_polling"}
    assert report.summary["interrupt_required"] in {"true", "false"}
    assert report.summary["reopen_target"] in {"none", "control_packet", "control_packet_snapshot_section", "control_packet_and_driver_signal"}


def test_v134tc_program_control_loop_signal_feed_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TCAShareInternalHotNewsProgramControlLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["control_loop_signal_feed"] == "read_ready_internal_only"
    assert rows["loop_signal_mode"] == "materialized"
    assert rows["interrupt_required"] == "materialized"
    assert rows["reopen_target"] == "materialized"
