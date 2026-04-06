from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oi_a_share_shadow_execution_stub_replacement_precondition_audit_v1 import (
    V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer,
)


def test_v134oi_stub_replacement_precondition_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["precondition_count"] == 5
    assert report.summary["unsatisfied_count"] == 1
    assert report.summary["foundation_only_count"] == 4
    assert report.summary["promotable_now_count"] == 14


def test_v134oi_stub_replacement_precondition_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer(repo_root).analyze()
    rows = {row["precondition"]: row for row in report.rows}

    assert rows["market_context_coverage_closed"]["precondition_state"] == "unsatisfied"
    assert rows["daily_market_promotion_nonblocked"]["precondition_state"] == "satisfied_foundation_only"
    assert rows["cost_model_foundation_ready"]["precondition_state"] == "satisfied_foundation_only"
    assert rows["shadow_stub_replacement_lane_materialized"]["precondition_state"] == "satisfied_foundation_only"
