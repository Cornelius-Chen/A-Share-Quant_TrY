from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mu_a_share_execution_binding_blocker_stack_reaudit_v1 import (
    V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer,
)


def test_v134mu_execution_binding_reaudit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer(repo_root).analyze()

    assert report.summary["blocker_count"] == 6
    assert report.summary["source_blocker_count"] == 1
    assert report.summary["replay_blocker_count"] == 2


def test_v134mu_execution_binding_reaudit_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MUAShareExecutionBindingBlockerStackReauditV1Analyzer(repo_root).analyze()
    rows = {row["blocker_id"]: row for row in report.blocker_rows}
    assert rows["source_promotion_preconditions_unsatisfied"]["blocker_layer"] == "source_activation"
    assert rows["replay_market_context_boundary_residuals"]["blocker_layer"] == "replay"
    assert rows["replay_execution_journal_stub_only"]["blocker_layer"] == "replay"
