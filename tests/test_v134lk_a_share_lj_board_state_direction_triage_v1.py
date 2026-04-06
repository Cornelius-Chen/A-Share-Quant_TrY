from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lk_a_share_lj_board_state_direction_triage_v1 import (
    V134LKAShareLJBoardStateDirectionTriageV1Analyzer,
)


def test_v134lk_board_state_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LKAShareLJBoardStateDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["board_state_row_count"] == 18
    assert (
        report.summary["authoritative_status"]
        == "board_state_derivation_complete_enough_to_freeze_as_bootstrap_single_board_surface"
    )


def test_v134lk_board_state_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LKAShareLJBoardStateDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["residual_backlog"] == "retain_for_future_multi_board_and_full_daily_derivation_expansion"
