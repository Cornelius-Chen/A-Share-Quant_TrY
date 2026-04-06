from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pr_a_share_shadow_calendar_alignment_candidate_audit_v1 import (
    V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer,
)


def test_v134pr_shadow_calendar_alignment_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_row_count"] == 1
    assert report.summary["same_timestamp_event_count"] == 2
    assert report.summary["nearest_prior_trade_date"] == "2026-03-27"


def test_v134pr_shadow_calendar_alignment_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer(repo_root).analyze()
    row = report.rows[0]

    assert row["decision_trade_date"] == "2026-03-28"
    assert row["candidate_effective_trade_date"] == "2026-03-27"
    assert row["timestamp_policy"] == "retain_visible_event_timestamp"
