from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lj_a_share_board_state_foundation_audit_v1 import (
    V134LJAShareBoardStateFoundationAuditV1Analyzer,
)


def test_v134lj_board_state_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LJAShareBoardStateFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["board_state_row_count"] == 18
    assert report.summary["lockout_worthy_count"] >= 1
    assert report.summary["unlock_worthy_count"] >= 1


def test_v134lj_board_state_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LJAShareBoardStateFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["board_state_surface"]["component_state"] == "materialized_bootstrap_single_board"
    assert rows["board_state_residual_backlog"]["component_state"] == "materialized_named_residuals"
