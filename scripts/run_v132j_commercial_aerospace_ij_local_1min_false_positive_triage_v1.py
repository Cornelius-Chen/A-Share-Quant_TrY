from pathlib import Path

from a_share_quant.strategy.v132j_commercial_aerospace_ij_local_1min_false_positive_triage_v1 import (
    V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132j_commercial_aerospace_ij_local_1min_false_positive_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
