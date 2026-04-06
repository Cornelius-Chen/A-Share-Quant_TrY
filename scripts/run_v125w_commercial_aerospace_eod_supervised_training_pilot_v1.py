from pathlib import Path

from a_share_quant.strategy.v125w_commercial_aerospace_eod_supervised_training_pilot_v1 import (
    V125WCommercialAerospaceEODSupervisedTrainingPilotAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125WCommercialAerospaceEODSupervisedTrainingPilotAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125w_commercial_aerospace_eod_supervised_training_pilot_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
