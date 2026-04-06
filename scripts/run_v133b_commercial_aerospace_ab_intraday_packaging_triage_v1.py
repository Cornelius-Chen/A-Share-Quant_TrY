from pathlib import Path

from a_share_quant.strategy.v133b_commercial_aerospace_ab_intraday_packaging_triage_v1 import (
    V133BCommercialAerospaceABIntradayPackagingTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133BCommercialAerospaceABIntradayPackagingTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133b_commercial_aerospace_ab_intraday_packaging_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
