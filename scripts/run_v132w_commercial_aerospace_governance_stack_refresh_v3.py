from pathlib import Path

from a_share_quant.strategy.v132w_commercial_aerospace_governance_stack_refresh_v3 import (
    V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132w_commercial_aerospace_governance_stack_refresh_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
