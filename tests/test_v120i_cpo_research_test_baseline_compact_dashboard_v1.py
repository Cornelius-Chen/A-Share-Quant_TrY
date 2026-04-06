from pathlib import Path

from a_share_quant.strategy.v120i_cpo_research_test_baseline_compact_dashboard_v1 import (
    CpoResearchTestBaselineCompactDashboardAnalyzer,
)


def test_v120i_compact_dashboard_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = CpoResearchTestBaselineCompactDashboardAnalyzer(repo_root=repo_root).analyze()
    png_path = repo_root / payload["summary"]["compact_dashboard_png"]
    assert png_path.exists()
    assert payload["summary"]["action_count"] > 0
