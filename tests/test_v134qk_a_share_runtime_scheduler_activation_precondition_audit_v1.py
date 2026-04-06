from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1 import (
    V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer,
)


def test_v134qk_runtime_scheduler_precondition_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["precondition_count"] == 5
    assert report.summary["unsatisfied_count"] == 1
    assert report.summary["priority_runtime_candidate_count"] == 1
    assert report.summary["lane_row_count"] == 1


def test_v134qk_runtime_scheduler_precondition_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(repo_root).analyze()
    rows = {row["precondition"]: row for row in report.rows}

    assert rows["single_runtime_candidate_isolated"]["precondition_state"] == "satisfied"
    assert rows["scheduler_runtime_activation"]["precondition_state"] == "unsatisfied"
    assert rows["scheduler_stub_replacement_lane_materialized"]["precondition_state"] == "satisfied_foundation_only"
