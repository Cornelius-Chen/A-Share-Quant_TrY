from pathlib import Path

from a_share_quant.strategy.v131n_commercial_aerospace_mn_5min_direction_triage_v1 import (
    V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131n_commercial_aerospace_mn_5min_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
