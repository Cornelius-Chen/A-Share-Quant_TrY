from pathlib import Path

from a_share_quant.strategy.v134en_program_master_status_card_v4 import (
    V134ENProgramMasterStatusCardV4Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134eo_program_master_governance_triage_v4 import (
    V134EOProgramMasterGovernanceTriageV4Analyzer,
)


def test_v134eo_program_master_governance_triage_v4() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134ENProgramMasterStatusCardV4Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134en_program_master_status_card_v4",
        result=status,
    )
    result = V134EOProgramMasterGovernanceTriageV4Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "open_program_frontier_with_intraday_add_supervision_only_and_reduce_frozen"
    )
