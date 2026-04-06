from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oy_a_share_information_center_terminal_handoff_package_v1 import (
    V134OYAShareInformationCenterTerminalHandoffPackageV1Analyzer,
)


def test_information_center_terminal_handoff_package_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OYAShareInformationCenterTerminalHandoffPackageV1Analyzer(repo_root).analyze()

    assert result.summary["handoff_component_count"] == 4
    assert result.summary["foundation_complete_count"] == 13
    assert result.summary["source_pending_step_count"] == 1
    assert result.summary["replay_promotable_now_count"] == 14
    assert result.summary["replay_shadow_eligible_subset_count"] == 15


def test_information_center_terminal_handoff_package_states() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OYAShareInformationCenterTerminalHandoffPackageV1Analyzer(repo_root).analyze()

    states = {row["handoff_component"]: row["handoff_state"] for row in result.handoff_rows}
    assert states["information_center_core"] == "build_complete_enough"
    assert states["source_internal_manual"] == "single_runtime_scheduler_governance_opening_followthrough_lane"
    assert states["replay_promotion_lane"] == "shadow_execution_eligible_subset_controlled_recheck_lane"
