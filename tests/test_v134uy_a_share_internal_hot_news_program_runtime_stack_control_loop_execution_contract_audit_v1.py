from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134uy_a_share_internal_hot_news_program_runtime_stack_control_loop_execution_contract_audit_v1 import (
    V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Analyzer,
)


def test_v134uy_runtime_stack_control_loop_execution_contract_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Analyzer(repo_root).analyze()

    assert report.summary["contract_row_count"] == 1
    assert report.summary["runtime_consumer_mode"] in {
        "passive_polling_only",
        "elevate_polling",
        "elevate_and_reopen",
        "interrupt_and_reopen",
    }
    assert report.summary["contract_action"] in {
        "keep_runtime_stack_passive_polling",
        "elevate_runtime_stack_loop_and_reopen_target",
        "elevate_runtime_stack_polling_only",
        "reopen_runtime_stack_target_without_interrupt",
        "interrupt_runtime_stack_loop_and_reopen_target",
    }


def test_v134uy_runtime_stack_control_loop_execution_contract_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UYAShareInternalHotNewsProgramRuntimeStackControlLoopExecutionContractAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_execution_contract"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode"] == "materialized"
    assert rows["contract_action"] == "materialized"
    assert rows["sleep_strategy_seconds"] == "materialized"
