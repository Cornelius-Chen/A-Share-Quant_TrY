from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qd_a_share_qc_shadow_execution_candidate_journal_direction_triage_v1 import (
    V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Analyzer,
)


def test_v134qd_shadow_execution_candidate_journal_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_execution_candidate_journal_overlay_is_useful_for_internal_replay_build_but_must_remain_shadow_only"
    )


def test_v134qd_shadow_execution_candidate_journal_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["promotion_boundary"]["direction"] == (
        "do_not_treat_the_candidate_journal_overlay_as_execution_opening_or_live_like_authority"
    )
