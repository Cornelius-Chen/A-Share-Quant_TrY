from pathlib import Path

from a_share_quant.strategy.v134cx_program_master_status_card_v2 import (
    V134CXProgramMasterStatusCardV2Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CXProgramMasterStatusCardV2Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cx_program_master_status_card_v2",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
