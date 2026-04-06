from pathlib import Path

from a_share_quant.strategy.v133i_program_master_status_card_v1 import (
    V133IProgramMasterStatusCardAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133IProgramMasterStatusCardAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133i_program_master_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
