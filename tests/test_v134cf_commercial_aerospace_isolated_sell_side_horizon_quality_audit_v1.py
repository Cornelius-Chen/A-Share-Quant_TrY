from pathlib import Path

from a_share_quant.strategy.v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1 import (
    V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer,
)


def test_v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer(repo_root).analyze()

    assert result.summary["executed_order_count"] == 12
    assert result.summary["same_day_protected_mark_to_close_total"] > 15000
    assert result.summary["net_horizon_pnl_if_held_1d"] < 0
    assert result.summary["net_horizon_pnl_if_held_3d"] > 0
    assert result.summary["net_horizon_pnl_if_held_5d"] < 0
    assert any(row["symbol"] == "300342" and float(row["horizon_pnl_if_held_1d"]) < 0 for row in result.session_rows)
