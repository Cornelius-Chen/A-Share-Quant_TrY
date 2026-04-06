from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uw_a_share_internal_hot_news_program_runtime_stack_control_loop_runtime_envelope_change_signal_audit_v1 import (
    V134UWAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeChangeSignalAuditV1Analyzer,
)


def test_v134uw_runtime_stack_control_loop_runtime_envelope_change_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UWAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["runtime_consumer_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["reopen_target_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v134uw_runtime_stack_control_loop_runtime_envelope_change_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UWAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_runtime_envelope_change_signal"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode_change"] == "materialized"
    assert rows["runtime_attention_level_change"] == "materialized"
    assert rows["poll_interval_change"] == "materialized"
