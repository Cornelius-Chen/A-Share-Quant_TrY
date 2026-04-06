from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ui_a_share_internal_hot_news_program_runtime_stack_supervision_contract_audit_v1 import (
    V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer,
)


def test_v134ui_runtime_stack_supervision_contract_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer(repo_root).analyze()

    assert report.summary["contract_row_count"] == 1
    assert report.summary["supervision_loop_mode"] in {
        "steady_supervision_loop",
        "tight_supervision_loop",
        "interrupt_supervision_loop",
    }
    assert report.summary["contract_action"] in {
        "keep_steady_supervision",
        "tighten_supervision_loop",
        "elevate_supervision_only",
        "reopen_target_without_interrupt",
        "interrupt_supervision_loop_and_reopen_target",
    }


def test_v134ui_runtime_stack_supervision_contract_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134UIAShareInternalHotNewsProgramRuntimeStackSupervisionContractAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_stack_supervision_contract"] == "read_ready_internal_only"
    assert rows["supervision_loop_mode"] == "materialized"
    assert rows["contract_action"] == "materialized"
    assert rows["sleep_strategy_seconds"] == "materialized"
