from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oh_a_share_og_manual_review_workpack_direction_triage_v1 import (
    V134OHAShareOGManualReviewWorkpackDirectionTriageV1Analyzer,
)


def test_v134oh_manual_review_workpack_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OHAShareOGManualReviewWorkpackDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "batch_one_manual_closure_should_now_use_consolidated_workpack_surface"
    )


def test_v134oh_manual_review_workpack_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OHAShareOGManualReviewWorkpackDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["workpack_usage"]["direction"].startswith("use_single_workpack_surface")
    assert rows["promotion_gate"]["direction"].startswith("keep_allowlist_promotion_closed")
