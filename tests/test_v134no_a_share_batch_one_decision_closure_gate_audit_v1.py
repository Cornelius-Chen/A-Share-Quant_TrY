from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134no_a_share_batch_one_decision_closure_gate_audit_v1 import (
    V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer,
)


def test_v134no_batch_one_closure_gate_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["decision_unit_count"] == 4
    assert report.summary["pending_manual_unit_count"] == 0
    assert report.summary["manual_decision_completed_count"] == 4
    assert report.summary["promotable_now_count"] == 0


def test_v134no_batch_one_closure_gate_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NOAShareBatchOneDecisionClosureGateAuditV1Analyzer(repo_root).analyze()
    rows = {row["closure_component"]: row for row in report.rows}

    assert rows["primary_host_family"]["closure_state"] == "manual_decision_completed"
    assert rows["promotion_gate"]["closure_state"] == "closed_pending_runtime_promotion"
