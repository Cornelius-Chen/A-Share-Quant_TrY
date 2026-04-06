from pathlib import Path

from a_share_quant.strategy.v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1 import (
    V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer,
)


def test_v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer(repo_root).analyze()

    assert result.summary["trade_date_count"] == 67
    assert result.summary["symbol_count"] == 12
    assert result.summary["ledger_row_count"] == 584
    assert result.summary["positive_start_of_day_row_count"] == 558
    assert result.summary["same_day_new_lots_row_count"] == 55
    assert result.summary["same_day_primary_action_row_count"] == 190

    rows = result.ledger_rows
    assert any(
        row["trade_date"] == "20260113"
        and row["symbol"] == "000738"
        and row["start_of_day_quantity"] == 0
        and row["same_day_open_quantity"] == 4000
        and row["eligible_intraday_sell_quantity"] == 0
        for row in rows
    )
    assert any(
        row["trade_date"] == "20260120"
        and row["symbol"] == "300342"
        and row["start_of_day_quantity"] == 3000
        and row["same_day_reduce_quantity"] == 2200
        for row in rows
    )
