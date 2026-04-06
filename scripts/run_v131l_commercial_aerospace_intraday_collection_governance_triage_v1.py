from pathlib import Path

from a_share_quant.strategy.v131l_commercial_aerospace_intraday_collection_governance_triage_v1 import (
    V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131LCommercialAerospaceIntradayCollectionGovernanceTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131l_commercial_aerospace_intraday_collection_governance_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
