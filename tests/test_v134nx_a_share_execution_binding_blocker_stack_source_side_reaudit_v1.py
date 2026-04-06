from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nx_a_share_execution_binding_blocker_stack_source_side_reaudit_v1 import (
    V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer,
)


def test_v134nx_execution_blocker_source_side_reaudit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer(repo_root).analyze()

    assert report.summary["blocker_count"] == 6
    assert report.summary["source_blocker_count"] == 1


def test_v134nx_execution_blocker_source_side_reaudit_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NXAShareExecutionBindingBlockerStackSourceSideReauditV1Analyzer(repo_root).analyze()
    rows = {row["blocker_id"]: row for row in report.blocker_rows}

    assert "source_manual_review_records_pending" not in rows
    assert rows["source_promotion_preconditions_unsatisfied"]["blocking_reason"] == "unsatisfied_precondition_count = 1"
