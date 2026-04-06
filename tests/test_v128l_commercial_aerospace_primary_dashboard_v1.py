from pathlib import Path

from a_share_quant.strategy.v128l_commercial_aerospace_primary_dashboard_v1 import (
    V128LCommercialAerospacePrimaryDashboardAnalyzer,
)


def test_v128l_commercial_aerospace_primary_dashboard_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128LCommercialAerospacePrimaryDashboardAnalyzer(repo_root).analyze()

    assert result.summary["variant"] == "tail_weakdrift_full"
    assert round(float(result.summary["final_equity"]), 4) == 1309426.5555
    assert round(float(result.summary["max_drawdown"]), 8) == 0.09309927
    assert int(result.summary["executed_order_count"]) == 211
    assert len(result.grouped_action_rows) > 0
    assert len(result.top_drawdown_rows) == 3

    dashboard_png = repo_root / result.summary["dashboard_png"]
    daily_csv = repo_root / result.summary["daily_state_csv"]
    orders_csv = repo_root / result.summary["orders_csv"]
    grouped_csv = repo_root / result.summary["grouped_actions_csv"]

    assert dashboard_png.exists()
    assert daily_csv.exists()
    assert orders_csv.exists()
    assert grouped_csv.exists()
