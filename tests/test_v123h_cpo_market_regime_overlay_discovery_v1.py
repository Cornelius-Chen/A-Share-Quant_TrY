from pathlib import Path

from a_share_quant.strategy.v123h_cpo_market_regime_overlay_discovery_v1 import (
    V123HCpoMarketRegimeOverlayDiscoveryAnalyzer,
)


def test_v123h_picks_liquidity_drought_regime() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123HCpoMarketRegimeOverlayDiscoveryAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["chosen_score_name"] == "liquidity_drought_regime_score"
    assert result.summary["chosen_q75_balanced_accuracy"] > 0.56

