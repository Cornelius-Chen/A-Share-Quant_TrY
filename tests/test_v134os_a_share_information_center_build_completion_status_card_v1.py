from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134os_a_share_information_center_build_completion_status_card_v1 import (
    V134OSAShareInformationCenterBuildCompletionStatusCardV1Analyzer,
)


def test_information_center_build_completion_status_card_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OSAShareInformationCenterBuildCompletionStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["foundation_complete_count"] == 13
    assert result.summary["manual_closure_pending_count"] == 1
    assert result.summary["replay_promotable_now_count"] == 14
    assert result.summary["replay_shadow_eligible_subset_count"] == 15
    assert result.summary["global_blocker_count"] == 6


def test_information_center_build_completion_status_card_states() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OSAShareInformationCenterBuildCompletionStatusCardV1Analyzer(repo_root).analyze()

    states = {row["component"]: row["component_state"] for row in result.status_rows}
    assert states["information_center_core"] == "build_complete_enough"
    assert states["source_internal_manual"] == "single_runtime_opening_review_lane_pending_scheduler_and_governance_after_build"
    assert states["replay_promotion"] == "shadow_execution_eligible_subset_materialized_after_shadow_overlay_recheck"
