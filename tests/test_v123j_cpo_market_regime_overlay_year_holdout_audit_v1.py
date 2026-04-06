from pathlib import Path

from a_share_quant.strategy.v123h_cpo_market_regime_overlay_discovery_v1 import write_report as write_v123h
from a_share_quant.strategy.v123h_cpo_market_regime_overlay_discovery_v1 import (
    V123HCpoMarketRegimeOverlayDiscoveryAnalyzer,
)
from a_share_quant.strategy.v123j_cpo_market_regime_overlay_year_holdout_audit_v1 import (
    V123JCpoMarketRegimeOverlayYearHoldoutAuditAnalyzer,
)


def test_v123j_year_holdout_keeps_signal_alive() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    write_v123h(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123h_cpo_market_regime_overlay_discovery_v1",
        result=V123HCpoMarketRegimeOverlayDiscoveryAnalyzer(repo_root=repo_root).analyze(),
    )
    result = V123JCpoMarketRegimeOverlayYearHoldoutAuditAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["chosen_score_name"] == "liquidity_drought_regime_score"
    assert result.summary["evaluability"] == "not_evaluable_single_year_only"
