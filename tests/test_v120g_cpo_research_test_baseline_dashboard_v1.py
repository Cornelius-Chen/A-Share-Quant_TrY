from pathlib import Path

from a_share_quant.strategy.v120g_cpo_research_test_baseline_dashboard_v1 import (
    CpoResearchTestBaselineDashboardAnalyzer,
)


def test_v120g_dashboard_outputs_exist() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = CpoResearchTestBaselineDashboardAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    summary = result.summary
    assert summary["research_test_final_equity"] > 1000000.0
    assert summary["research_test_max_drawdown"] > 0.0

    dashboard_png = repo_root / summary["dashboard_png"]
    daily_csv = repo_root / summary["daily_state_csv"]
    action_csv = repo_root / summary["action_strip_csv"]

    assert dashboard_png.exists()
    assert daily_csv.exists()
    assert action_csv.exists()
