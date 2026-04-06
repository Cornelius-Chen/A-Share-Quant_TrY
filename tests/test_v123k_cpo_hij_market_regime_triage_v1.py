from a_share_quant.strategy.v123k_cpo_hij_market_regime_triage_v1 import (
    V123KCpoHijMarketRegimeTriageAnalyzer,
)


def test_v123k_freezes_market_regime_as_explanatory_only() -> None:
    result = V123KCpoHijMarketRegimeTriageAnalyzer().analyze()
    assert result.summary["authoritative_status"] == "explanatory_only"
    assert result.summary["majority_vote"]["explanatory_only"] == 3

