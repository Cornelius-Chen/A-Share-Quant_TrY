from pathlib import Path

from a_share_quant.strategy.v130h_transfer_program_gh_same_plane_freeze_triage_v1 import (
    V130HTransferProgramGHSamePlaneFreezeTriageAnalyzer,
)


def test_v130h_transfer_program_gh_same_plane_freeze_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130HTransferProgramGHSamePlaneFreezeTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == "freeze_transfer_program_and_do_not_open_a_new_board_worker_yet"
    assert any(row["direction"] == "new_board_worker" and row["status"] == "blocked" for row in result.direction_rows)
