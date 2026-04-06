from pathlib import Path

from a_share_quant.strategy.v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1 import (
    V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer,
    write_report as write_ledger_report,
)
from a_share_quant.strategy.v134ca_commercial_aerospace_bz_holdings_ledger_direction_triage_v1 import (
    V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Analyzer,
)


def test_v134ca_commercial_aerospace_bz_holdings_ledger_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    ledger = V134BZCommercialAerospaceStartOfDayHoldingsLedgerV1Analyzer(repo_root).analyze()
    write_ledger_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bz_commercial_aerospace_start_of_day_holdings_ledger_v1",
        result=ledger,
    )

    result = V134CACommercialAerospaceBZHoldingsLedgerDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_holdings_ledger_and_open_isolated_sell_side_shadow_lane_next"
    )
    assert result.summary["ledger_row_count"] == 584
    assert result.summary["collision_session_count"] == 8
