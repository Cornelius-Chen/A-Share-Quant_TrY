from pathlib import Path

from a_share_quant.strategy.v134en_program_master_status_card_v4 import V134ENProgramMasterStatusCardV4Analyzer


def test_v134en_program_master_status_card_v4() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ENProgramMasterStatusCardV4Analyzer(repo_root).analyze()

    assert result.summary["next_frontier"] == "intraday_add"
    assert result.summary["next_frontier_state"] == "opened_supervision_only"
    assert result.summary["opened_supervision_line_count"] == 1
