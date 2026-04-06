from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sq_a_share_internal_hot_news_program_status_change_signal_audit_v1 import (
    V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer,
)


def test_v134sq_program_status_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p0", "p1", "p2"}
    assert report.summary["session_phase_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["program_consumer_gate_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["program_driver_action_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["program_driver_transition_class"] in {
        "no_previous_baseline",
        "stable",
        "activation_rotation",
        "hard_block_rotation",
        "noncritical_rotation",
    }
    assert report.summary["driver_escalation_priority"] in {"p0", "p1", "p2"}


def test_v134sq_program_status_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_status_change_signal"] == "read_ready_internal_only"
    assert rows["signal_priority"] == "materialized"
    assert rows["session_change"] == "materialized"
    assert rows["consumer_gate_change"] == "materialized"
    assert rows["driver_action_change"] == "materialized"
    assert rows["driver_transition"] == "materialized"
    assert rows["driver_escalation"] == "materialized"
