from pathlib import Path

from a_share_quant.strategy.v127j_commercial_aerospace_ijk_derisk_budget_triage_v1 import (
    V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V127JCommercialAerospaceIJKDeriskBudgetTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127j_commercial_aerospace_ijk_derisk_budget_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
