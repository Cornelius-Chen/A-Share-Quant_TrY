from pathlib import Path

from a_share_quant.strategy.v133f_commercial_aerospace_intraday_reopen_change_gate_v1 import (
    V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V133FCommercialAerospaceIntradayReopenChangeGateAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133f_commercial_aerospace_intraday_reopen_change_gate_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
