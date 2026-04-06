from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iq_commercial_aerospace_expanded_symbol_universe_carrier_search_audit_v1 import (
    V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer,
)


def test_v134iq_expanded_symbol_universe_carrier_search_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer(repo_root).analyze()

    assert result.summary["expanded_formal_symbol_count"] == 3
    assert result.summary["outside_named_formal_symbol_count"] == 3
    assert result.summary["priority_second_carrier_candidate_count"] == 1
    assert result.summary["formal_strength_watch_count"] == 1

    by_symbol = {row["symbol"]: row for row in result.symbol_rows}
    assert by_symbol["000738"]["carrier_search_label"] == "priority_second_carrier_search_candidate"
    assert by_symbol["600118"]["carrier_search_label"] == "formal_strength_watch_not_yet_carrier"
    assert by_symbol["002085"]["carrier_search_label"] == "formal_noncandidate"
