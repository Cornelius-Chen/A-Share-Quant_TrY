from pathlib import Path

from a_share_quant.strategy.v130l_transfer_program_gap_closure_scenarios_v1 import (
    V130LTransferProgramGapClosureScenariosAnalyzer,
)


def test_v130l_transfer_program_gap_closure_scenarios_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130LTransferProgramGapClosureScenariosAnalyzer(repo_root).analyze()

    assert result.summary["single_action_reopen_candidate_count"] == 1
    assert result.summary["nearest_reopen_sector_id"] == "BK0808"
    assert result.scenario_rows[0]["sector_id"] == "BK0808"
    assert result.scenario_rows[0]["single_action_reopen_possible"] is True
