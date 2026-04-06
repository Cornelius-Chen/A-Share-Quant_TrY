from pathlib import Path

from a_share_quant.strategy.v120h_cpo_research_test_baseline_single_panel_dashboard_v1 import (
    CpoResearchTestBaselineSinglePanelDashboardAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CpoResearchTestBaselineSinglePanelDashboardAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v120h_cpo_research_test_baseline_single_panel_dashboard_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

