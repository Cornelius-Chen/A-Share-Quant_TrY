from pathlib import Path

from a_share_quant.strategy.v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1 import (
    CpoResearchTestBaselineTopDrawdownDashboardAnalyzer,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = CpoResearchTestBaselineTopDrawdownDashboardAnalyzer(repo_root=repo_root).analyze()
    print(repo_root / payload["summary"]["top_drawdown_dashboard_png"])


if __name__ == "__main__":
    main()

