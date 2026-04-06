from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lr_a_share_lq_review_activation_direction_triage_v1 import (
    V134LRAShareLQReviewActivationDirectionTriageV1Analyzer,
)


def test_v134lr_review_activation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LRAShareLQReviewActivationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["review_registry_count"] == 3
    assert (
        report.summary["authoritative_status"]
        == "review_activation_complete_enough_to_freeze_and_shift_into_live_like_gate_readiness"
    )


def test_v134lr_review_activation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LRAShareLQReviewActivationDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "shift_into_live_like_gate_readiness_audit_using_source_activation_review_and_governance_as_inputs"
    )
