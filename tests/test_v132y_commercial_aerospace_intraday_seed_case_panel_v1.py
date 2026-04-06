from pathlib import Path

from a_share_quant.strategy.v132y_commercial_aerospace_intraday_seed_case_panel_v1 import (
    V132YCommercialAerospaceIntradaySeedCasePanelAnalyzer,
)


def test_v132y_intraday_seed_case_panel_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132YCommercialAerospaceIntradaySeedCasePanelAnalyzer(repo_root).analyze()

    assert report.summary["seed_case_count"] == 6
    assert len(report.case_rows) == 6

