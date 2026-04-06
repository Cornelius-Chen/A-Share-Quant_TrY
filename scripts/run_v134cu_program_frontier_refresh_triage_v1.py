from pathlib import Path

from a_share_quant.strategy.v134ct_commercial_aerospace_frontier_status_card_v1 import (
    V134CTCommercialAerospaceFrontierStatusCardV1Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134cu_program_frontier_refresh_triage_v1 import (
    V134CUProgramFrontierRefreshTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134CTCommercialAerospaceFrontierStatusCardV1Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ct_commercial_aerospace_frontier_status_card_v1",
        result=status,
    )
    result = V134CUProgramFrontierRefreshTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cu_program_frontier_refresh_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
