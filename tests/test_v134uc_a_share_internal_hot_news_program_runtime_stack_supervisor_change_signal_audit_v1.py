from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uc_a_share_internal_hot_news_program_runtime_stack_supervisor_change_signal_audit_v1 import (
    V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer,
)


def test_v134uc_runtime_stack_supervisor_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["supervisor_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["program_health_state_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v134uc_runtime_stack_supervisor_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_supervisor_change_signal"] == "read_ready_internal_only"
    assert rows["supervisor_mode_change"] == "materialized"
    assert rows["program_health_state_change"] == "materialized"
    assert rows["runtime_consumer_mode_change"] == "materialized"
    assert rows["scheduler_loop_signal_mode_change"] == "materialized"
    assert rows["orchestration_loop_signal_mode_change"] == "materialized"
