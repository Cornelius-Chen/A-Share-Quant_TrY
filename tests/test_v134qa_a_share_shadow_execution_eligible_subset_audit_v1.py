from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qa_a_share_shadow_execution_eligible_subset_audit_v1 import (
    V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer,
)


def test_v134qa_shadow_execution_eligible_subset_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer(repo_root).analyze()

    assert report.summary["total_stub_row_count"] == 17
    assert report.summary["eligible_subset_count"] == 15
    assert report.summary["excluded_boundary_count"] == 2


def test_v134qa_shadow_execution_eligible_subset_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["shadow_execution_eligible_subset"]["component_state"] == "materialized_shadow_only_eligible_subset"
