from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nt_a_share_ns_manual_review_record_direction_triage_v1 import (
    V134NTAShareNSManualReviewRecordDirectionTriageV1Analyzer,
)


def test_v134nt_manual_review_record_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NTAShareNSManualReviewRecordDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "manual_review_records_should_be_filled_before_any_batch_one_promotion"
    )


def test_v134nt_manual_review_record_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NTAShareNSManualReviewRecordDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["record_order"]["direction"].startswith("fill_primary_host_family_record_first")
    assert rows["promotion_dependency"]["direction"].startswith("keep_allowlist_promotion_closed")
