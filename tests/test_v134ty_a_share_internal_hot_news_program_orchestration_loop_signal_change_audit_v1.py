from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ty_a_share_internal_hot_news_program_orchestration_loop_signal_change_audit_v1 import (
    V134TYAShareInternalHotNewsProgramOrchestrationLoopSignalChangeAuditV1Analyzer,
)


def test_v134ty_program_orchestration_loop_signal_change_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TYAShareInternalHotNewsProgramOrchestrationLoopSignalChangeAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["orchestration_loop_signal_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["reopen_target_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v134ty_program_orchestration_loop_signal_change_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TYAShareInternalHotNewsProgramOrchestrationLoopSignalChangeAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["orchestration_loop_signal_change"] == "read_ready_internal_only"
    assert rows["loop_signal_mode_change"] == "materialized"
    assert rows["signal_priority_change"] == "materialized"
    assert rows["reopen_target_change"] == "materialized"
