from pathlib import Path

from a_share_quant.strategy.v130i_transfer_program_reopen_trigger_protocol_v1 import (
    V130ITransferProgramReopenTriggerProtocolAnalyzer,
)


def test_v130i_transfer_program_reopen_trigger_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130ITransferProgramReopenTriggerProtocolAnalyzer(repo_root).analyze()

    assert result.summary["reopen_ready_count"] == 0
    assert all(row["reopen_ready"] is False for row in result.trigger_rows)
    assert any(row["sector_id"] == "BK0808" and row["same_plane_symbol_trigger_met"] is False for row in result.trigger_rows)
