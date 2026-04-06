from pathlib import Path

from a_share_quant.strategy.v134en_program_master_status_card_v4 import (
    V134ENProgramMasterStatusCardV4Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ENProgramMasterStatusCardV4Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134en_program_master_status_card_v4",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
