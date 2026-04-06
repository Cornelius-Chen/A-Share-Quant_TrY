from pathlib import Path

from a_share_quant.strategy.v134dd_program_master_status_card_v3 import (
    V134DDProgramMasterStatusCardV3Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134de_program_master_governance_triage_v3 import (
    V134DEProgramMasterGovernanceTriageV3Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134DDProgramMasterStatusCardV3Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134dd_program_master_status_card_v3",
        result=status,
    )
    result = V134DEProgramMasterGovernanceTriageV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134de_program_master_governance_triage_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
