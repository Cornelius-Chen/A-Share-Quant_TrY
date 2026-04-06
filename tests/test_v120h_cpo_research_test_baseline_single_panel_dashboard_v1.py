from pathlib import Path

from a_share_quant.strategy.v120h_cpo_research_test_baseline_single_panel_dashboard_v1 import (
    CpoResearchTestBaselineSinglePanelDashboardAnalyzer,
)


def test_v120h_single_panel_dashboard_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CpoResearchTestBaselineSinglePanelDashboardAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    png_path = repo_root / result.summary["single_panel_dashboard_png"]
    assert png_path.exists()
