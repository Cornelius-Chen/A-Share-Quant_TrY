from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ua_a_share_internal_hot_news_program_runtime_stack_supervisor_surface_audit_v1 import (
    V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer,
)


def test_v134ua_runtime_stack_supervisor_surface_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["surface_row_count"] == 1
    assert report.summary["supervisor_mode"] in {
        "interrupt_supervision",
        "tight_supervision",
        "elevated_supervision",
        "steady_supervision",
    }


def test_v134ua_runtime_stack_supervisor_surface_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_supervisor_surface"] == "read_ready_internal_only"
    assert rows["supervisor_mode"] == "materialized"
    assert rows["runtime_consumer_mode"] == "materialized"
    assert rows["scheduler_loop_signal_mode"] == "materialized"
    assert rows["orchestration_loop_signal_mode"] == "materialized"
