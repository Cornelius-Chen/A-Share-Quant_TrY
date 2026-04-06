from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sm_a_share_internal_hot_news_program_change_action_signal_audit_v1 import (
    V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer,
)


def test_v134sm_program_change_action_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p0", "p2"}
    assert report.summary["session_action_gate_state"] in {
        "no_previous_baseline",
        "action_changed",
        "stable",
    }


def test_v134sm_program_change_action_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_change_action_signal"] == "read_ready_internal_only"
    assert rows["global_program_action_mode_state"] == "materialized"
    assert rows["session_action_gate_state"] == "materialized"
