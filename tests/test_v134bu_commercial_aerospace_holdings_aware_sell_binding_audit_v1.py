from pathlib import Path

from a_share_quant.strategy.v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1 import (
    V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer,
)


def test_v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer(repo_root).analyze()

    assert result.summary["broader_hit_session_count"] == 24
    assert result.summary["positive_start_quantity_count"] == 16
    assert result.summary["fully_funded_overlap_count"] == 1
    assert result.summary["underfunded_overlap_count"] == 15
    assert result.summary["no_actual_holding_count"] == 8
    assert result.summary["same_day_primary_collision_count"] == 8

    rows = result.session_rows
    assert any(
        row["trade_date"] == "20260120"
        and row["symbol"] == "300342"
        and row["holding_status"] == "fully_funded_overlap"
        for row in rows
    )
    assert any(
        row["trade_date"] == "20260113"
        and row["symbol"] == "000738"
        and row["holding_status"] == "no_actual_holding"
        for row in rows
    )
