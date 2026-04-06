from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lv_a_share_lu_live_like_view_direction_triage_v1 import (
    V134LVAShareLULiveLikeViewDirectionTriageV1Analyzer,
)


def test_v134lv_live_like_view_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LVAShareLULiveLikeViewDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["event_state_row_count"] == 17
    assert (
        report.summary["authoritative_status"]
        == "live_like_view_materialization_complete_enough_to_freeze_and_reaudit_gate"
    )


def test_v134lv_live_like_view_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LVAShareLULiveLikeViewDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_gate_review"] == "rerun_live_like_gate_readiness_with_view_materialization_gap_closed"
