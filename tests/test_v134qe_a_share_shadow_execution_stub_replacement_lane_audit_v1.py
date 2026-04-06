from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qe_a_share_shadow_execution_stub_replacement_lane_audit_v1 import (
    V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer,
)


def test_v134qe_shadow_execution_stub_replacement_lane_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer(repo_root).analyze()

    assert report.summary["stub_row_count"] == 17
    assert report.summary["lane_overlay_row_count"] == 15
    assert report.summary["excluded_boundary_count"] == 2


def test_v134qe_shadow_execution_stub_replacement_lane_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QEAShareShadowExecutionStubReplacementLaneAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["shadow_stub_replacement_lane"]["component_state"] == "shadow_only_overlay_lane_materialized"
