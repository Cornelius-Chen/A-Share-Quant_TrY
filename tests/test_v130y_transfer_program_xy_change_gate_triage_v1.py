from pathlib import Path

from a_share_quant.strategy.v130y_transfer_program_xy_change_gate_triage_v1 import (
    V130YTransferProgramXYChangeGateTriageAnalyzer,
)


def test_v130y_transfer_program_xy_change_gate_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130YTransferProgramXYChangeGateTriageAnalyzer(repo_root).analyze()

    assert result.summary["artifact_count"] == 5
    assert result.summary["authoritative_status"] == "static_data_gate_installed_for_transfer_program"
