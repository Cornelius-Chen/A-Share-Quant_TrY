from pathlib import Path

from a_share_quant.strategy.v134eh_commercial_aerospace_intraday_add_frontier_opening_v1 import (
    V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eh_commercial_aerospace_intraday_add_frontier_opening_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
