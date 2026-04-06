from pathlib import Path

from a_share_quant.strategy.v128r_commercial_aerospace_primary_timechain_dashboard_v1 import (
    V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128r_commercial_aerospace_primary_timechain_dashboard_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
