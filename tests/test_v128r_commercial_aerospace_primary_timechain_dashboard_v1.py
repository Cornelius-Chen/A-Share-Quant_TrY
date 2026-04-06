from pathlib import Path

from a_share_quant.strategy.v128r_commercial_aerospace_primary_timechain_dashboard_v1 import (
    V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer,
)


def test_v128r_commercial_aerospace_primary_timechain_dashboard_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128RCommercialAerospacePrimaryTimechainDashboardAnalyzer(repo_root).analyze()

    assert result.summary["variant"] == "tail_weakdrift_full"
    assert round(float(result.summary["final_equity"]), 4) == 1309426.5555
    assert round(float(result.summary["max_drawdown"]), 8) == 0.09309927
    assert int(result.summary["executed_order_count"]) == 211
    assert int(result.summary["suspicious_buy_order_count"]) == 0
    assert len(result.grouped_action_rows) > 0
    assert len(result.top_drawdown_rows) == 3

    target_row = next(row for row in result.grouped_action_rows if row["execution_trade_date"] == "20260113")
    assert target_row["signal_trade_dates"] == "20260112"
    assert target_row["pre_open_event_status"] == "no_decisive_event"
    assert target_row["signal_execution_display"] == "01-12>01-13"

    dashboard_png = repo_root / result.summary["dashboard_png"]
    grouped_csv = repo_root / result.summary["timechain_grouped_actions_csv"]

    assert dashboard_png.exists()
    assert grouped_csv.exists()
