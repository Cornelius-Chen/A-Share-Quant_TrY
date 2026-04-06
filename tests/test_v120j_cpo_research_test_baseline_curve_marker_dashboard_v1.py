from pathlib import Path

from a_share_quant.strategy.v120j_cpo_research_test_baseline_curve_marker_dashboard_v1 import (
    CpoResearchTestBaselineCurveMarkerDashboardAnalyzer,
)


def test_v120j_curve_marker_dashboard_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = CpoResearchTestBaselineCurveMarkerDashboardAnalyzer(repo_root=repo_root).analyze()
    png_path = repo_root / payload["summary"]["curve_marker_dashboard_png"]
    assert png_path.exists()
    assert payload["summary"]["marker_count"] > 0
