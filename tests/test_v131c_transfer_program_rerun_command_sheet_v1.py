from pathlib import Path

from a_share_quant.strategy.v131c_transfer_program_rerun_command_sheet_v1 import (
    V131CTransferProgramRerunCommandSheetAnalyzer,
)


def test_v131c_transfer_program_rerun_command_sheet_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131CTransferProgramRerunCommandSheetAnalyzer(repo_root).analyze()

    assert result.summary["rerun_chain_count"] == 3
    assert result.summary["authoritative_status"] == "rerun_command_sheet_ready_but_only_to_be_used_after_change_gate_opens"
    assert any(row["rerun_chain"] == "v130n_to_v130w" for row in result.chain_rows)
