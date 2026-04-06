from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ti_a_share_internal_hot_news_program_runtime_execution_contract_audit_v1 import (
    V134TIAShareInternalHotNewsProgramRuntimeExecutionContractAuditV1Analyzer,
)


def test_v134ti_runtime_execution_contract_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TIAShareInternalHotNewsProgramRuntimeExecutionContractAuditV1Analyzer(repo_root).analyze()

    assert report.summary["contract_row_count"] == 1
    assert report.summary["runtime_consumer_mode"] in {
        "interrupt_and_reopen",
        "elevate_and_reopen",
        "elevate_polling",
        "passive_polling_only",
    }
    assert report.summary["contract_action"] in {
        "interrupt_loop_and_reopen_target",
        "elevate_and_reopen_target",
        "elevate_polling_only",
        "reopen_target_without_interrupt",
        "keep_passive_polling",
    }


def test_v134ti_runtime_execution_contract_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TIAShareInternalHotNewsProgramRuntimeExecutionContractAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_execution_contract"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode"] == "materialized"
    assert rows["contract_action"] == "materialized"
    assert rows["sleep_strategy"] == "materialized"
    assert rows["backoff_mode"] == "materialized"
