from pathlib import Path

from a_share_quant.strategy.v134cx_program_master_status_card_v2 import (
    V134CXProgramMasterStatusCardV2Analyzer,
)


def test_v134cx_program_master_status_card_v2() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CXProgramMasterStatusCardV2Analyzer(repo_root).analyze()

    assert result.summary["line_count"] == 6
    assert result.summary["deferred_line_count"] == 1
    assert any(
        row["program_line"] == "commercial_aerospace_next_frontier"
        and row["status"] == "deferred"
        and row["current_variant"] == "intraday_add"
        for row in result.status_rows
    )

