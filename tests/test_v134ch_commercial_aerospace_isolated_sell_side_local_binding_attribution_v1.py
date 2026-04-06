from pathlib import Path

from a_share_quant.strategy.v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1 import (
    V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer,
)


def test_v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer(repo_root).analyze()

    assert result.summary["executed_order_count"] == 12
    assert result.summary["best_same_day_symbol"] == "300342"
    assert result.summary["worst_3d_rebound_symbol"] == "300342"
    assert result.summary["positive_3d_rebound_case_count"] == 4
    assert result.summary["top_3d_rebound_case"] == "20260120 300342"

