from pathlib import Path

from a_share_quant.strategy.v125s_commercial_aerospace_point_in_time_regime_proxy_v1 import (
    V125SCommercialAerospacePointInTimeRegimeProxyAnalyzer,
)


def test_v125s_builds_point_in_time_regime_proxy() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125SCommercialAerospacePointInTimeRegimeProxyAnalyzer(repo_root).analyze()
    assert result.summary["date_count"] > 0
    assert "impulse_expansion_proxy" in result.summary["proxy_regime_counts"] or "weak_drift_chop_proxy" in result.summary["proxy_regime_counts"]
