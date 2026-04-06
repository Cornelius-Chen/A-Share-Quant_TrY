from pathlib import Path

from a_share_quant.strategy.v130j_transfer_program_ij_reopen_governance_triage_v1 import (
    V130JTransferProgramIJReopenGovernanceTriageAnalyzer,
)


def test_v130j_transfer_program_ij_reopen_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130JTransferProgramIJReopenGovernanceTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == "freeze_transfer_program_but_keep_explicit_reopen_governance"
    assert any(row["direction"] == "new_board_worker" and row["status"] == "blocked_until_reopen_ready" for row in result.direction_rows)
