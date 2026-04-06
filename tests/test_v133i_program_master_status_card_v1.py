from pathlib import Path

from a_share_quant.strategy.v133i_program_master_status_card_v1 import (
    V133IProgramMasterStatusCardAnalyzer,
)


def test_v133i_program_master_status_card_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133IProgramMasterStatusCardAnalyzer(repo_root).analyze()

    assert report.summary["line_count"] == 5
    assert report.summary["frozen_line_count"] >= 4

