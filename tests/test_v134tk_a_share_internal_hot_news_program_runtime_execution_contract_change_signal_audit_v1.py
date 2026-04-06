from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134tk_a_share_internal_hot_news_program_runtime_execution_contract_change_signal_audit_v1 import (
    V134TKAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalAuditV1Analyzer,
)


def test_v134tk_runtime_execution_contract_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TKAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["runtime_consumer_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["contract_action_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v134tk_runtime_execution_contract_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TKAShareInternalHotNewsProgramRuntimeExecutionContractChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["runtime_execution_contract_change_signal"] == "read_ready_internal_only"
    assert rows["runtime_consumer_mode_change"] == "materialized"
    assert rows["contract_action_change"] == "materialized"
    assert rows["sleep_strategy_change"] == "materialized"
    assert rows["backoff_mode_change"] == "materialized"
