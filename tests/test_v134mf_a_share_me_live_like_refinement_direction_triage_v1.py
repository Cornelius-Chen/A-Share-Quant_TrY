from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mf_a_share_me_live_like_refinement_direction_triage_v1 import (
    V134MFAShareMELiveLikeRefinementDirectionTriageV1Analyzer,
)


def test_v134mf_live_like_refinement_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MFAShareMELiveLikeRefinementDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "live_like_gate_refined_and_kept_blocked_until_selective_activation_and_execution_shift"
    )


def test_v134mf_live_like_refinement_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MFAShareMELiveLikeRefinementDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["source_activation"]["direction"] == "freeze_policy_bound_network_fetch_without_runtime_activation"
