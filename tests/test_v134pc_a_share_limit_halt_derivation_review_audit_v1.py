from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pc_a_share_limit_halt_derivation_review_audit_v1 import (
    V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer,
)


def test_v134pc_limit_halt_derivation_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["promotion_review_row_count"] == 17
    assert report.summary["raw_daily_candidate_cover_count"] == 14
    assert report.summary["limit_halt_materialized_count"] == 14
    assert report.summary["promotable_now_count"] == 14
    assert report.summary["blocked_by_limit_halt_derivation_count"] == 0


def test_v134pc_limit_halt_derivation_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["limit_halt_derivation_state"]["component_state"] == "semantic_surface_materialized_for_recheck"
