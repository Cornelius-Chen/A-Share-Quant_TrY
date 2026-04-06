from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)


def test_v134nu_allowlist_precondition_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["precondition_count"] == 4
    assert report.summary["unsatisfied_count"] == 1
    assert report.summary["promotable_now_count"] == 0


def test_v134nu_allowlist_precondition_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(repo_root).analyze()

    rows = {row["precondition"]: row for row in report.rows}
    assert rows["manual_review_records_filled"]["precondition_state"] == "satisfied"
    assert rows["runtime_candidate_promotable"]["precondition_state"] == "unsatisfied"
