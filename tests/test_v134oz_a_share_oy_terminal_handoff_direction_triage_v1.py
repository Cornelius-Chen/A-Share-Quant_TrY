from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oz_a_share_oy_terminal_handoff_direction_triage_v1 import (
    V134OZAShareOYTerminalHandoffDirectionTriageV1Analyzer,
)


def test_information_center_terminal_handoff_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OZAShareOYTerminalHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["handoff_component_count"] == 4
    assert result.summary["foundation_complete_count"] == 13


def test_information_center_terminal_handoff_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OZAShareOYTerminalHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["source_lane"] == "advance_only_by_manual_operator_execution_from_stage_1_checklist"
    assert directions["replay_lane"] == "advance_only_after_replay_internal_build_preconditions_move"
