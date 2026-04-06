from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134li_a_share_lh_contradiction_direction_triage_v1 import (
    V134LIAShareLHContradictionDirectionTriageV1Analyzer,
)


def test_v134li_contradiction_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LIAShareLHContradictionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["duplicate_merge_candidate_count"] > 0
    assert (
        report.summary["authoritative_status"]
        == "contradiction_resolution_complete_enough_to_freeze_as_bootstrap"
    )


def test_v134li_contradiction_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LIAShareLHContradictionDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["semantic_divergence"] == "retain_review_queue_for_future_real_conflict_sources"
