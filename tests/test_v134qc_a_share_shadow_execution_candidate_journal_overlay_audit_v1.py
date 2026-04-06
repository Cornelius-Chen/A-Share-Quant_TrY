from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qc_a_share_shadow_execution_candidate_journal_overlay_audit_v1 import (
    V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer,
)


def test_v134qc_shadow_execution_candidate_journal_overlay_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer(repo_root).analyze()

    assert report.summary["overlay_row_count"] == 15
    assert report.summary["excluded_boundary_count"] == 2


def test_v134qc_shadow_execution_candidate_journal_overlay_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["shadow_execution_candidate_journal_overlay"]["component_state"] == (
        "materialized_shadow_only_candidate_journal_overlay"
    )
