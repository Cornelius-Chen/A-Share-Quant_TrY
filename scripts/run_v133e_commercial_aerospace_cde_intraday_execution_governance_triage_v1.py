from pathlib import Path

from a_share_quant.strategy.v133e_commercial_aerospace_cde_intraday_execution_governance_triage_v1 import (
    V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133e_commercial_aerospace_cde_intraday_execution_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
