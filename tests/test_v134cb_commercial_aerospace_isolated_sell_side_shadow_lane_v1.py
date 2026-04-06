from pathlib import Path

from a_share_quant.strategy.v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1 import (
    V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer,
)


def test_v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CBCommercialAerospaceIsolatedSellSideShadowLaneV1Analyzer(repo_root).analyze()

    assert result.summary["broader_hit_session_count"] == 24
    assert result.summary["executed_session_count"] == 12
    assert result.summary["skipped_no_inventory_count"] == 8
    assert result.summary["skipped_mild_count"] == 4
    assert result.summary["order_count"] == 12
    assert result.summary["clipped_reconciliation_count"] >= 1

    assert any(
        row["trade_date"] == "20260113"
        and row["symbol"] == "000738"
        and row["skip_reason"] == "no_eligible_start_of_day_inventory"
        for row in result.session_rows
    )
    assert any(
        row["trade_date"] == "20260120"
        and row["symbol"] == "300342"
        and row["sell_quantity"] == 3000
        for row in result.order_rows
    )
