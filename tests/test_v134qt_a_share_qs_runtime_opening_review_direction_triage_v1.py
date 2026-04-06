from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qt_a_share_qs_runtime_opening_review_direction_triage_v1 import (
    V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Analyzer,
)


def test_v134qt_runtime_opening_review_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["review_row_count"] == 1
    assert report.summary["scheduler_pending_count"] == 1
    assert report.summary["governance_closed_count"] == 1


def test_v134qt_runtime_opening_review_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "single_row_scheduler_governance_review_surface" in rows["opening_review_surface"]
    assert "retain_silent_opening_disallowed" in rows["opening_boundary"]
