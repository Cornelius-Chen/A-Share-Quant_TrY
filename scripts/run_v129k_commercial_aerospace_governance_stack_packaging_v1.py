from pathlib import Path

from a_share_quant.strategy.v129k_commercial_aerospace_governance_stack_packaging_v1 import (
    V129KCommercialAerospaceGovernanceStackPackagingAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129KCommercialAerospaceGovernanceStackPackagingAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129k_commercial_aerospace_governance_stack_packaging_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
