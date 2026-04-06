from pathlib import Path

from a_share_quant.strategy.v120i_cpo_research_test_baseline_compact_dashboard_v1 import (
    CpoResearchTestBaselineCompactDashboardAnalyzer,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = CpoResearchTestBaselineCompactDashboardAnalyzer(repo_root=repo_root).analyze()
    print(repo_root / payload["summary"]["compact_dashboard_png"])


if __name__ == "__main__":
    main()

