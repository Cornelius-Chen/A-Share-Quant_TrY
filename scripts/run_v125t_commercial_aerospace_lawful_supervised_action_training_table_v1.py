from pathlib import Path

from a_share_quant.strategy.v125t_commercial_aerospace_lawful_supervised_action_training_table_v1 import (
    V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer,
    write_csv_file,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125t_commercial_aerospace_lawful_supervised_action_training_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_lawful_supervised_action_training_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
