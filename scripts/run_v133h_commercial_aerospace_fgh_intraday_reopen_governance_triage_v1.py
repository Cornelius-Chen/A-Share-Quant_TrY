from pathlib import Path

from a_share_quant.strategy.v133h_commercial_aerospace_fgh_intraday_reopen_governance_triage_v1 import (
    V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133h_commercial_aerospace_fgh_intraday_reopen_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
