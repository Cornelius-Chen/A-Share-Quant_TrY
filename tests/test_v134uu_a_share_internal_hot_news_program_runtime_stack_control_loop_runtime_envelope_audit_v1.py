from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uu_a_share_internal_hot_news_program_runtime_stack_control_loop_runtime_envelope_audit_v1 import (
    V134UUAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeAuditV1Analyzer,
)


def test_v134uu_runtime_stack_control_loop_runtime_envelope_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UUAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeAuditV1Analyzer(repo_root).analyze()

    assert report.summary["envelope_row_count"] == 1
    assert report.summary["runtime_consumer_mode"] in {
        "passive_polling_only",
        "elevate_polling",
        "elevate_and_reopen",
        "interrupt_and_reopen",
    }
    assert report.summary["runtime_attention_level"] in {"low", "medium", "high"}


def test_v134uu_runtime_stack_control_loop_runtime_envelope_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UUAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_runtime_envelope"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode"] == "materialized"
    assert rows["runtime_attention_level"] == "materialized"
    assert rows["suggested_poll_interval"] == "materialized"
