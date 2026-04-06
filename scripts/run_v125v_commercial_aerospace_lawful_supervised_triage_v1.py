from pathlib import Path

from a_share_quant.strategy.v125v_commercial_aerospace_lawful_supervised_triage_v1 import (
    V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125v_commercial_aerospace_lawful_supervised_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
