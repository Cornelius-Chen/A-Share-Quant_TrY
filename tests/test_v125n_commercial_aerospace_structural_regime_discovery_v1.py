from pathlib import Path

from a_share_quant.strategy.v125n_commercial_aerospace_structural_regime_discovery_v1 import (
    V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer,
)


def test_v125n_discovers_four_regimes() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(repo_root).analyze()
    assert result.summary["regime_count"] == 4
