from pathlib import Path

from a_share_quant.strategy.v130g_transfer_program_same_plane_support_freeze_v1 import (
    V130GTransferProgramSamePlaneSupportFreezeAnalyzer,
)


def test_v130g_transfer_program_same_plane_support_freeze_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130GTransferProgramSamePlaneSupportFreezeAnalyzer(repo_root).analyze()

    assert result.summary["same_plane_ready_count"] == 0
    rows = {row["sector_id"]: row for row in result.candidate_rows}
    assert rows["BK0808"]["v6_symbol_count"] == 1
    assert rows["BK0808"]["bridge_only"] is True
