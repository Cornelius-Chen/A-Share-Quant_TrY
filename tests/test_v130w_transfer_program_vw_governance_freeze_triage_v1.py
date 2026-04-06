from pathlib import Path

from a_share_quant.strategy.v130w_transfer_program_vw_governance_freeze_triage_v1 import (
    V130WTransferProgramVWGovernanceFreezeTriageAnalyzer,
)


def test_v130w_transfer_program_vw_governance_freeze_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130WTransferProgramVWGovernanceFreezeTriageAnalyzer(repo_root).analyze()

    assert result.summary["closest_candidate_sector_id"] == "BK0808"
    assert result.summary["decisive_watch_symbol"] == "600118"
    assert result.summary["authoritative_status"] == "stop_same_data_board_reanalysis_and_wait_for_new_local_support"
