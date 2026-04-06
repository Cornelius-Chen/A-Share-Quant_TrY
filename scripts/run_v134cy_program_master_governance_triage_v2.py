from pathlib import Path

from a_share_quant.strategy.v134cx_program_master_status_card_v2 import (
    V134CXProgramMasterStatusCardV2Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134cy_program_master_governance_triage_v2 import (
    V134CYProgramMasterGovernanceTriageV2Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134CXProgramMasterStatusCardV2Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cx_program_master_status_card_v2",
        result=status,
    )
    result = V134CYProgramMasterGovernanceTriageV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cy_program_master_governance_triage_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
