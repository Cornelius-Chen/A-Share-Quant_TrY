from pathlib import Path

from a_share_quant.strategy.v133k_program_reopen_playbook_v1 import (
    V133KProgramReopenPlaybookAnalyzer,
)


def test_v133k_program_reopen_playbook_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133KProgramReopenPlaybookAnalyzer(repo_root).analyze()

    assert report.summary["line_count"] == 4
    assert report.summary["intraday_missing_artifact_count"] == 3

