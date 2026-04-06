from pathlib import Path

from a_share_quant.strategy.v134cx_program_master_status_card_v2 import (
    V134CXProgramMasterStatusCardV2Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134cy_program_master_governance_triage_v2 import (
    V134CYProgramMasterGovernanceTriageV2Analyzer,
)


def test_v134cy_program_master_governance_triage_v2() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134CXProgramMasterStatusCardV2Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cx_program_master_status_card_v2",
        result=status,
    )

    result = V134CYProgramMasterGovernanceTriageV2Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_program_lines_with_reduce_complete_and_intraday_add_deferred"
    )
    assert result.summary["deferred_line_count"] == 1
