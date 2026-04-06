from pathlib import Path

from a_share_quant.strategy.v134dd_program_master_status_card_v3 import V134DDProgramMasterStatusCardV3Analyzer


def test_v134dd_program_master_status_card_v3() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134DDProgramMasterStatusCardV3Analyzer(repo_root).analyze()

    assert result.summary["next_frontier"] == "intraday_add"
    assert result.summary["opening_gate_count"] == 9
    assert result.summary["silent_opening_allowed"] is False
    assert any(
        row["program_line"] == "commercial_aerospace_next_frontier"
        and row["status"] == "deferred"
        and row["opening_posture"] == "prelaunch_only"
        for row in result.status_rows
    )
