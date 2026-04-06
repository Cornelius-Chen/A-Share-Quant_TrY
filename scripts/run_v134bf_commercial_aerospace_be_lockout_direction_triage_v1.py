from pathlib import Path

from a_share_quant.strategy.v134bf_commercial_aerospace_be_lockout_direction_triage_v1 import (
    V134BFCommercialAerospaceBELockoutDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BFCommercialAerospaceBELockoutDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bf_commercial_aerospace_be_lockout_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
