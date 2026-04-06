from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134te_a_share_internal_hot_news_program_control_loop_runtime_envelope_audit_v1 import (
    V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer,
)


def test_v134te_program_control_loop_runtime_envelope_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer(repo_root).analyze()

    assert report.summary["envelope_row_count"] == 1
    assert report.summary["runtime_consumer_mode"] in {
        "interrupt_and_reopen",
        "elevate_and_reopen",
        "elevate_polling",
        "passive_polling_only",
    }
    assert report.summary["runtime_attention_level"] in {"high", "medium", "low"}


def test_v134te_program_control_loop_runtime_envelope_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_envelope"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode"] == "materialized"
    assert rows["runtime_attention_level"] == "materialized"
    assert rows["suggested_poll_interval"] == "materialized"
