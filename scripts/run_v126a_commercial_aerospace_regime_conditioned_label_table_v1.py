from pathlib import Path

from a_share_quant.strategy.v126a_commercial_aerospace_regime_conditioned_label_table_v1 import (
    V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer,
    write_csv_file,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126a_commercial_aerospace_regime_conditioned_label_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_regime_conditioned_label_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
