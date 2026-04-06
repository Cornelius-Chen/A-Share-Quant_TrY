from pathlib import Path

from a_share_quant.strategy.v132n_commercial_aerospace_mn_local_1min_concentration_triage_v1 import (
    V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132n_commercial_aerospace_mn_local_1min_concentration_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
