from pathlib import Path

from a_share_quant.strategy.v132d_commercial_aerospace_cd_local_1min_seed_direction_triage_v1 import (
    V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132d_commercial_aerospace_cd_local_1min_seed_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
