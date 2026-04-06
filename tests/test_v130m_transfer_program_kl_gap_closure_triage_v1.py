from pathlib import Path

from a_share_quant.strategy.v130m_transfer_program_kl_gap_closure_triage_v1 import (
    V130MTransferProgramKLGapClosureTriageAnalyzer,
)


def test_v130m_transfer_program_kl_gap_closure_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130MTransferProgramKLGapClosureTriageAnalyzer(repo_root).analyze()

    assert result.summary["nearest_candidate_sector_id"] == "BK0808"
    assert result.summary["authoritative_status"] == "keep_transfer_program_frozen_and_prioritize_gap_closure_monitoring_over_worker_creation"
    assert any(row["sector_id"] == "BK0808" and row["direction"] == "monitor_closely_but_do_not_reopen" for row in result.triage_rows)
