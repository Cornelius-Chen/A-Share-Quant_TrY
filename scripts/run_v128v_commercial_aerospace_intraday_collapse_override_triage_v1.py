from pathlib import Path

from a_share_quant.strategy.v128v_commercial_aerospace_intraday_collapse_override_triage_v1 import (
    V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128v_commercial_aerospace_intraday_collapse_override_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
