from pathlib import Path

from a_share_quant.strategy.v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1 import (
    CpoResearchTestBaselineTopDrawdownDashboardAnalyzer,
)


def test_v120k_top_drawdown_dashboard_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = CpoResearchTestBaselineTopDrawdownDashboardAnalyzer(repo_root=repo_root).analyze()
    png_path = repo_root / payload["summary"]["top_drawdown_dashboard_png"]
    assert png_path.exists()
    assert payload["summary"]["top_drawdown_count"] == 3
