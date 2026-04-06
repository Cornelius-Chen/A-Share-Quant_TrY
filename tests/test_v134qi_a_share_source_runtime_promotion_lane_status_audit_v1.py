from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qi_a_share_source_runtime_promotion_lane_status_audit_v1 import (
    V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer,
)


def test_v134qi_source_runtime_promotion_lane_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer(repo_root).analyze()

    assert report.summary["priority_runtime_candidate_count"] == 1
    assert report.summary["lane_row_count"] == 1
    assert report.summary["excluded_runtime_row_count"] == 2
    assert report.summary["unsatisfied_precondition_count"] == 1
    assert report.summary["promotable_now_count"] == 0


def test_v134qi_source_runtime_promotion_lane_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QIAShareSourceRuntimePromotionLaneStatusAuditV1Analyzer(repo_root).analyze()
    rows = {row["runtime_component"]: row for row in report.rows}

    assert rows["source_manual_closure"]["runtime_state"] == "completed"
    assert rows["first_runtime_candidate_lane"]["runtime_state"] == "single_candidate_pending_scheduler_activation"
    assert rows["runtime_stub_replacement_lane"]["runtime_state"] == "materialized_foundation_only"
